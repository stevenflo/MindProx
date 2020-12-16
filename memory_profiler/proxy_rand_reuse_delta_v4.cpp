#include <algorithm>
#include <iostream>
#include <fstream>
#include <string>
#include <inttypes.h>
#include <stdlib.h>
#include <math.h>
#include <sstream>
#include <assert.h>
#include <functional>

#include <list>
#include <map>
#include <vector>

//#define DEBUG 1
//#define DEBUG_GEN 1

#define MAX_STREAMS 100000
#define MAX_MB_REUSE 4096
#define MAX_OFFSET_REUSE 262144
#define MAX_DELTA 7

#define MACROBLOCK_SIZE_BITS 12
#define MACROBLOCK_SIZE (1<<MACROBLOCK_SIZE_BITS)
#define MACROBLOCK_MASK ~((1<<MACROBLOCK_SIZE_BITS)-1)

#define PHASE_LEN 100000
#define MAX_INIT_ELEMS 30

using namespace std;

unsigned long long num_elems = 0;
bool DEBUG = false;
bool DEBUG_GEN = false; //true;

class DELTA_ENTRY;
class DELTA_TABLES;

std::map<unsigned, DELTA_TABLES> global_delta_tables;
typedef std::map<unsigned, DELTA_TABLES>::iterator GDT_IT;

class Stream_Replay {
  public:
	bool valid;
	uint64_t idx;
	uint64_t addr;

	Stream_Replay() {
		valid = false;
		idx = 0;
		addr = 0;
	}

	Stream_Replay(uint64_t _idx) {
                valid = false;
                idx = _idx;
                addr = 0;
        }

	void set_addr(uint64_t _addr) {
		valid = true;
		addr = _addr;	
	}

	bool get_valid() {
		return valid;
	}

	uint64_t get_addr() {
		return addr;
	}

	void print_entry(std::ostream* os) {
		assert(valid == true);
		*os << "1, " << addr << endl;
	}
};

class DELTA_ENTRY {
   public:
	std::map<int64_t, uint64_t> next_deltas;
	uint64_t num_times;
	std::string hashid;
	std::list<int64_t> hash_deltas;
	bool valid;
	int64_t most_freq_foll;

	DELTA_ENTRY() {
		next_deltas.clear();
		num_times = 0;
		hash_deltas.clear();
		valid = true;
		most_freq_foll = 0;
	}		

	~DELTA_ENTRY() {
		next_deltas.clear();
		hash_deltas.clear();
	}

	void set_hashid(std::string hs) {
		hashid = hs;
	}

	void invalidate_entry() {
		valid = false;
	}

	void init_delta_vals(int64_t dval) {
		hash_deltas.push_back(dval);
	}

	std::string get_partial_delta_string(int len) {
		std::string part_hash = "";
		std::ostringstream oss;
                int runn_loc = 0, start_loc = 0;
                if(hash_deltas.size() >= len) {
                	start_loc = hash_deltas.size() - len;
                }
                else {
			cout << "Hash val = " << hashid << ", hash_deltas.size() = " << hash_deltas.size() << ", partial hashlen = " << len << endl;
			assert(0);
		}

                assert(start_loc >= 0);

                for(std::list<int64_t>::iterator it = hash_deltas.begin(); it != hash_deltas.end(); it++) {
                	if(runn_loc >= start_loc) {
                        	//if(Stride_hashtable.size() == 0) {
                                //      cout << "Hashing Stride = " << (*it) << endl;
                                //}
				if(DEBUG) {
					cout << "Hash Delta " << (*it) << ", ";
				}
				oss << (*it);
				oss << ",";
			}
                        runn_loc++;
                }
                if(DEBUG) {
			cout << ", hash_deltas.size = " << hash_deltas.size() << endl;
                }
                part_hash += oss.str();
		if(DEBUG) {
			cout << "In get_partial_delta_string for hash " << hashid << ", partial len = " << len << ", partial hash = " << part_hash << endl;
		}
		return part_hash;
	}

	unsigned get_num_followers() {
		return next_deltas.size();
	}

	bool is_any_delta_valid(uint64_t last_addr, uint64_t comp_mb) {
		bool delta_found = false;
		uint64_t try_addr = 0;
		for(std::map<int64_t, uint64_t>::iterator it = next_deltas.begin(); it != next_deltas.end(); it++) {
			if(it->second > 0) {
				try_addr = last_addr + it->first;
                                if((try_addr >> MACROBLOCK_SIZE_BITS) == comp_mb) {
					delta_found = true;
					break;
				}
			}
		}
		return delta_found;
	}

	int64_t get_forced_delta(uint64_t temp_mb, uint64_t last_addr, bool* df) {
		bool delta_found = false;
		int64_t fd_delta_val = 0;
                uint64_t try_addr = 0;
                for(std::map<int64_t, uint64_t>::iterator it = next_deltas.begin(); it != next_deltas.end(); it++) {
                        if(it->second > 0) {
                                try_addr = last_addr + it->first;
                                if((try_addr >> MACROBLOCK_SIZE_BITS) == temp_mb) {
                                        delta_found = true;
					fd_delta_val = it->first;
                                        break;
                                }
                        }
                }
		*df = delta_found;
		return fd_delta_val;
	}

	int64_t get_rand_delta() {
		bool delta_found = false;
		int64_t this_delta = 0;

		int max_size = next_deltas.size();
		int rand_id;
		int ct = 0;

		int max_trys = 0;
		std::map<int64_t, uint64_t>::iterator it;
		while(delta_found == false) {
			rand_id = rand() % max_size;
			ct = 0;
			for(it = next_deltas.begin(); it != next_deltas.end(); it++) {
				if(ct == rand_id) {
					if(it->second > 0) {
						delta_found = true;
						this_delta = it->first;
						if(DEBUG_GEN) {
							cout << "In get_rand_delta, Found a random delta = " << this_delta << endl;
						}
					}
					break;
				}
				ct++;
			}

			max_trys++;
			if(max_trys == 100) {
				if(DEBUG_GEN) {
					cout << "In get_rand_delta, exhausted max_trys, using most freq foll = " << most_freq_foll << endl;
				}
				this_delta = most_freq_foll;
				delta_found = true;
			}
		}
		return this_delta;
	}

	void access(int64_t nd) {
		std::map<int64_t, uint64_t>::iterator it = next_deltas.find(nd);
		if(it == next_deltas.end()) {
			next_deltas[nd] = 1;
		}
		else {
			it->second += 1;
		}
		num_times += 1; 
	}

	int get_full_access_perc() {
		assert(num_times > 0);
		if(next_deltas.size() == 1) {
			return 100;
		}
		else {
			return 0;
		}
	}

	int64_t update_proxy(int64_t nd) {
		std::map<int64_t, uint64_t>::iterator it = next_deltas.find(nd);
		assert(it != next_deltas.end());
		if(DEBUG_GEN) {
			cout << "In update_proxy for hashid = " << hashid << ", next delta = " << nd << ", before next delta times = " << it->second << endl;
		}
		if(it->second > 0) {
			it->second -= 1;
		}
	}

	bool print_entry(std::ostream* os) {
		assert(num_times > 0);
		uint64_t max_val = 0;
		int64_t max_foll = 0;
		uint64_t tot_ct = 0;
		if(valid) {
			*os << "Hash_ID " << hashid << ": ";
			std::map<int64_t, uint64_t>::iterator it;
			for(it = next_deltas.begin(); it != next_deltas.end(); it++) {
				if(it->second > max_val) {
					max_val = it->second;
					max_foll = it->first;
				}
				//*os << it->first << " = " << ((it->second * 100)/num_times) << ", ";
				*os << it->first << " = " << it->second << ", ";
				tot_ct += it->second;
			}
			*os << "max follower = " << max_foll << ", entry count = " << tot_ct << endl;
			most_freq_foll = max_foll;
			return true;
		}
		return false;
	}
};

class DELTA_TABLES 
{	
   public:
	std::map<std::string, DELTA_ENTRY> next_deltas;
	typedef std::map<std::string, DELTA_ENTRY>::iterator ND_IT;
		
	int hist_len;

	DELTA_TABLES() {
		next_deltas.clear();
	}

	DELTA_TABLES(int len) {
		hist_len = len;
		next_deltas.clear();
	}

	~DELTA_TABLES() {
		next_deltas.clear();
	}

	void init_delta_vals(std::string hash, int64_t dval) {
		std::map<std::string, DELTA_ENTRY>::iterator ndit = next_deltas.find(hash);
		assert(ndit != next_deltas.end());
		if(DEBUG) {
			cout << "In init_delta_vals for hist_len = " << hist_len << ", hash = " << hash << ", dval = " << dval << endl;
		}
		ndit->second.init_delta_vals(dval);
	}

	bool access_full_perc(std::string hash) {
		bool full_access_bool = false;
		bool is_present = false;
		int full_access_perc = 0;

		std::map<std::string, DELTA_ENTRY>::iterator ndit = next_deltas.find(hash);

		if(ndit != next_deltas.end()) {
			is_present = true;
			full_access_perc = ndit->second.get_full_access_perc();
		}
		if(full_access_perc == 100) {
			full_access_bool = true;
		}
		if(DEBUG) {
			cout << "In access_full_perc, hash = " << hash << ", is_present = " << is_present << ", full_access_perc = " << full_access_perc << ", full_access_bool = " << full_access_bool << endl; 
		}
		return full_access_bool;
	}

	void update_table(std::string hash, int64_t ndelta) {
		std::map<std::string, DELTA_ENTRY>::iterator ndit = next_deltas.find(hash);
		if(ndit == next_deltas.end()) {
			DELTA_ENTRY den;
			den.set_hashid(hash);
			den.access(ndelta);
			next_deltas[hash] = den;
		}
		else {
			ndit->second.access(ndelta);
		}
	}

	void print_tables(std::ostream* os) {
		std::map<std::string, DELTA_ENTRY>::iterator ndit;
		uint64_t tot_count = 0;
		bool val_entry = false;
		uint64_t tot_entries = 0;

		for(ndit = next_deltas.begin(); ndit != next_deltas.end(); ndit++) {
			val_entry = ndit->second.print_entry(os);
			tot_count += ndit->second.num_times;
			if(val_entry) {
				tot_entries++;
			}
		}
		*os << "Total elem count = " << tot_count << ", tot table entries = " << tot_entries << endl;
	}
};

class MACRO_BLOCK_LOC {
   public:
	uint64_t mb_addr;
	std::list <int64_t> last_N_deltas;
	std::list <int64_t> first_N_deltas;
	std::list <int64_t> saved_first_N_deltas;

	uint64_t last_addr;
	uint64_t first_addr;
        uint64_t num_accesses;
	uint64_t first_proxy_gen;

	MACRO_BLOCK_LOC() {
		init();
	}		

	MACRO_BLOCK_LOC(uint64_t addr, uint64_t _mb) {
		init();
		mb_addr = _mb;
		last_addr = addr;
		first_addr = addr;
	}

	~MACRO_BLOCK_LOC() {
		last_N_deltas.clear();
                first_N_deltas.clear();
                saved_first_N_deltas.clear();
	}

	void init() {
		mb_addr = 0;
		last_N_deltas.clear();
		first_N_deltas.clear();
		saved_first_N_deltas.clear();
		num_accesses = 1;
		first_proxy_gen = false;
	}

	void reset() {
		last_N_deltas.clear();
		last_addr = 0;
	}

	void print_MB(std::ostream* os) {
		*os << "This MB " << mb_addr << ", num_accesses = " << num_accesses << ", first_addr = " << first_addr << ", List of first deltas = ";
		for(std::list <int64_t>::iterator it = first_N_deltas.begin(); it != first_N_deltas.end(); it++) {
			*os << *it << ", ";
		}
		*os << endl;
	}

	uint64_t get_first_address() {
		return first_addr;
	}

	bool is_first_access() {
		if(first_proxy_gen == false) {
			first_proxy_gen = true;
			assert(first_N_deltas.size() == saved_first_N_deltas.size());
			return true;
		}
		else {
			return false;
		}
	}

	uint64_t get_num_accesses() {
		return num_accesses;
	}

	void update_first_M_deltas(int64_t td) {
		if(first_N_deltas.size() < MAX_DELTA) {
			first_N_deltas.push_back(td);
			saved_first_N_deltas.push_back(td);
		}
	}

	bool reuse_first_addr() {	
		if(((first_addr + saved_first_N_deltas.front()) >> MACROBLOCK_SIZE_BITS) == mb_addr) {
			return true;
		}
		return false;
	}

	void reinit_first_addr() {
		first_N_deltas.clear();
		last_N_deltas.clear();
		last_addr = first_addr;

		for(std::list <int64_t>::iterator it = saved_first_N_deltas.begin(); it != saved_first_N_deltas.end(); it++) {
			first_N_deltas.push_back(*it);
		}
	}

	void access_mb(uint64_t addr) {
		assert (mb_addr == (addr >> MACROBLOCK_SIZE_BITS));
		int64_t this_delta = addr - last_addr;

		update_first_M_deltas(this_delta);

		if(DEBUG) {
			cout << "In access_mb, page = " << mb_addr << ", addr = " << addr << ", last_addr = " << last_addr << ", delta = " << this_delta << endl;
		}

		//compute string deltas (till max-length possible) and update global delta tables
                std::string hash_val = "";
		std::list<int64_t> list_of_deltas;
		list_of_deltas.clear();
                //std::ostringstream oss, oss1;
	        //std::hash<std::string> hash_fn;
		//size_t hash;
		int start_loc = 0;
		int runn_loc = 0;
		
		for(int i = 1; i <= MAX_DELTA; i++) {
			hash_val = "";		
			std::ostringstream oss;
			list_of_deltas.clear();
			if(DEBUG) {
				cout << "history length i = " << i << ", last_N_deltas.size() = " << last_N_deltas.size() << endl;
			}
			runn_loc = 0;
			if(last_N_deltas.size() >= i) {
				start_loc = last_N_deltas.size() - i; 	
			}
			else {
				continue;
			}

			assert(start_loc >= 0);
			
                        for(std::list<int64_t>::iterator it = last_N_deltas.begin(); it != last_N_deltas.end(); it++) {
				if(runn_loc >= start_loc) {
					//if(Stride_hashtable.size() == 0) {
					//      cout << "Hashing Stride = " << (*it) << endl;
					//}
					if(DEBUG) {
						cout << "Delta " << (*it) << ", ";
					}
					oss << (*it);
					oss << ",";
					list_of_deltas.push_back(*it);
					//hash_val = hash_val ^ (*it);
				}
				runn_loc++;
                        }
			if(DEBUG) {
				cout << ", list_of_deltas.size = " << list_of_deltas.size() << endl;
			}
                        hash_val += oss.str();
                        //hash = hash_fn(hash_val);
                        //oss1 << hash;
                        //hash_val = oss1.str();

			//Hash val for i delta length, update_table
			if(DEBUG) {
				cout << "   hash_val = " << hash_val << ", next delta = " << this_delta << endl;
			}
			GDT_IT git = global_delta_tables.find(i);
			if(git == global_delta_tables.end()) {
				DELTA_TABLES dtab = DELTA_TABLES(i);
				dtab.update_table(hash_val, this_delta);
				for(std::list<int64_t>::iterator lit = list_of_deltas.begin(); lit != list_of_deltas.end(); lit++) {
					dtab.init_delta_vals(hash_val, *lit);
				}
				global_delta_tables[i] = dtab;
			}
			else {
				std::map<std::string, DELTA_ENTRY>::iterator ndit = git->second.next_deltas.find(hash_val);
		                if(ndit != git->second.next_deltas.end()) {
					git->second.update_table(hash_val, this_delta);
				}
				else {
					git->second.update_table(hash_val, this_delta);
					for(std::list<int64_t>::iterator lit = list_of_deltas.begin(); lit != list_of_deltas.end(); lit++) {
						git->second.init_delta_vals(hash_val, *lit);
					}
				}
			}
			
		}
		
		if(last_N_deltas.size() == MAX_DELTA) {
			last_N_deltas.pop_front();
		}
		last_N_deltas.push_back(this_delta);
		last_addr = addr;

		num_accesses++;		
		if(DEBUG) {
			cout << "In access_mb for mb_addr " << mb_addr << ", last_N_deltas.size = " << last_N_deltas.size() << ", last_addr = " << last_addr << endl;
		}
	}

	int64_t get_delta(uint64_t addr) {
                return (addr - last_addr);
        }

	void proxy_access(int64_t this_delta, bool first_access, uint64_t addr) {
		if(!first_access) {
			if(last_N_deltas.size() == MAX_DELTA) {
				last_N_deltas.pop_front();
			}
			last_N_deltas.push_back(this_delta);
		}
		last_addr = addr;
		assert(num_accesses > 0);
		num_accesses--;
	}

	std::string get_partial_delta_string(int len) {
		std::string part_hash = "";
                std::ostringstream oss;
                int runn_loc = 0, start_loc = 0;
                if(last_N_deltas.size() >= len) {
                        start_loc = last_N_deltas.size() - len;
                }
                else {
                        cout << "last_N_deltas.size() = " << last_N_deltas.size() << ", partial hashlen = " << len << endl;
                        assert(0);
                }

                assert(start_loc >= 0);

                for(std::list<int64_t>::iterator it = last_N_deltas.begin(); it != last_N_deltas.end(); it++) {
                        if(runn_loc >= start_loc) {
                                if(DEBUG) {
                                        cout << "Last N Delta " << (*it) << ", ";
                                }
                                oss << (*it);
                                oss << ",";
                        }
                        runn_loc++;
                }
                if(DEBUG) {
                        cout << ", last_N_deltas.size = " << last_N_deltas.size() << endl;
                }
                part_hash += oss.str();
                if(DEBUG) {
                        cout << "In get_partial_delta_string for MB " << mb_addr << ", partial len = " << len << ", partial hash = " << part_hash << endl;
                }

                return part_hash;
	}
};

class LOCALITY_MJ
{
   public:
   	std::list<uint64_t> last_macroblock_list;
	typedef std::list<uint64_t>::iterator LMB_IT;

	std::map<uint64_t, MACRO_BLOCK_LOC*> per_MB_historytable;
        typedef std::map<uint64_t, MACRO_BLOCK_LOC*>::iterator PMB_DIT;

        std::vector<uint64_t> MB_reuse;
	std::vector<uint64_t> unique_mbs;
	std::vector<uint64_t> unique_mb_ct;

	std::vector<unsigned> unique_MB_reuse;
        std::vector<uint64_t> unique_MB_reuse_ct;

        std::list <uint64_t> init_addrs;
	std::list <uint64_t>  mb_list;

	std::ostream* os;

	LOCALITY_MJ() {
		last_macroblock_list.clear();
		per_MB_historytable.clear();
		global_delta_tables.clear();
		MB_reuse.clear();
		MB_reuse.resize(MAX_MB_REUSE + 1);
		for(int i = 0; i <= MAX_MB_REUSE; i++) {
			MB_reuse[i] = 0;
		} 
		unique_mbs.clear();
		unique_mb_ct.clear();
                unique_MB_reuse.clear();
                unique_MB_reuse_ct.clear();
                init_addrs.clear();
		mb_list.clear();
	}

	void set_streambuf(std::streambuf* buf) {
		os = new std::ostream(buf);
	}

	void print_reuse_info() {
                cout << "In print_reuse_info, MB_reuse ";
                for(int i = 0; i <= MAX_MB_REUSE; i++) {
                        if(MB_reuse[i] > 0) {
                                cout << "[" << i << "] = " << MB_reuse[i] << ", ";
                        }
                }
                cout << "\n";
        }

	void print_locality_info(unsigned phase_ct) {
		*os << "MJ_PLI: Phase Ct = " << phase_ct << ", Total number of elements accessed = " << num_elems << endl;
		*os << "MJ_PLI: Overall macroblock reuse stats:\n";
		uint64_t temp_reuse = 0;
                for(int i = 0; i <= MAX_MB_REUSE; i++) {
                        temp_reuse += MB_reuse[i];
                        if((i == 0) || (i == 1) || (i == 2) || (i == 8) || (i == 16) || (i == 32) || (i == 64) || (i == 128) || (i == 256) || (i == 512) || (i == 1024) || (i == 2048) || (i == (MAX_MB_REUSE - 1)) || (i == MAX_MB_REUSE)) {
                                *os << "[" << i << "] = " << temp_reuse << ", ";
                                temp_reuse = 0;
                        }
                }
		*os << "\n\n";

		*os << "Printing per macroblock information, per_MB_historytable size = " << per_MB_historytable.size() << "\n";

		for(PMB_DIT mit = per_MB_historytable.begin(); mit != per_MB_historytable.end(); mit++) {
                        mit->second->print_MB(os);
                }

		*os << "\n\n";

		*os << "MJ_PLI: Printing global delta table stats\n";

		for(GDT_IT git = global_delta_tables.begin(); git != global_delta_tables.end(); git++) {
			*os << "Global Delta length = " << git->first << endl;
			git->second.print_tables(os);
			*os << endl;
		}

		*os << "MJ_PLI: Num of unique MBs accessed = " << per_MB_historytable.size() << endl;

		manage_cascaded_tables();

		*os << "MJ_PLI: Printing UPDATED global delta table stats\n";

                for(GDT_IT git = global_delta_tables.begin(); git != global_delta_tables.end(); git++) {
                        *os << "Global Delta length = " << git->first << endl;
                        git->second.print_tables(os);
                        *os << endl;
                }

	}

	void manage_cascaded_tables() {
		GDT_IT git, git_low;
		std::map<std::string, DELTA_ENTRY>::iterator ndit;
		std::string part_hash = "";

		for(int i = MAX_DELTA; i > 1; i--) {  
			if(DEBUG) {
				cout << "\n\nMJ: In manage_cascaded_tables, delta length = " << i << endl;
			}

			part_hash = "";
			git = global_delta_tables.find(i);
			if(git != global_delta_tables.end()) {
				//for every entry in the git table
                		for(ndit = git->second.next_deltas.begin(); ndit != git->second.next_deltas.end(); ndit++) {
					if(DEBUG) {
						cout << "\nCurrent hash element = " << ndit->first << endl;
					}
					for(int j = i - 1; j > 0; j--) {
						part_hash = ndit->second.get_partial_delta_string(j);
						git_low = global_delta_tables.find(j);
						if(DEBUG) {
							cout << "MJ: Partial " << j << " length hash of element (" << ndit->first << ") = " << part_hash << endl;
						}
						//Compare the last N deltas of current level with previous level, if previous level val = 0, then invalidate git's delta entry
						if(git_low->second.access_full_perc(part_hash) == true) {
							if(DEBUG) {
								cout << "MJ: Partial hash has 100% prob. Invalidating current entry\n";
							}
							//Invalidate ndit entry
							ndit->second.invalidate_entry();
							break;
						}
					}
				}
			}
		}

		//For length 1 tables
		if(DEBUG) {
                	cout << "\n\nMJ: In manage_cascaded_tables, delta length = " << 1 << endl;
                }
		git = global_delta_tables.find(1);
                if(git != global_delta_tables.end()) {
                	//for every entry in the git table
	        	for(ndit = git->second.next_deltas.begin(); ndit != git->second.next_deltas.end(); ndit++) {
				//invalidate entries with non 100% values
				if(git->second.access_full_perc(ndit->first) == false) {
					if(DEBUG) {
						cout << "MJ: Partial hash for length 1 has 100% prob. Invalidating current entry\n";
					}
					//Invalidate ndit entry
					ndit->second.invalidate_entry();
				}
			}
		}
	}

	void phase_clear() {
		last_macroblock_list.clear();
		per_MB_historytable.clear();
		unique_mbs.clear();
		unique_mb_ct.clear();
		global_delta_tables.clear();
		for(int i = 0; i <= MAX_MB_REUSE; i++) {
                        MB_reuse[i] = 0;
                }
		unique_MB_reuse.clear();
                unique_MB_reuse_ct.clear();
		init_addrs.clear();
		mb_list.clear();
	}

	void prep4proxygen() {
		last_macroblock_list.clear();
		for(PMB_DIT mit = per_MB_historytable.begin(); mit != per_MB_historytable.end(); mit++) {
			mit->second->reset();
		}

                uint64_t temp_mb;
                for(int i = 0; i < unique_mbs.size(); i++) {
                        temp_mb = unique_mbs[i];
                        unique_mb_ct.push_back((per_MB_historytable[temp_mb])->get_num_accesses());
                }

                for(int i = 0; i <= MAX_MB_REUSE; i++) {
                        if(MB_reuse[i] > 0) {
                                unique_MB_reuse.push_back(i);
                                unique_MB_reuse_ct.push_back(MB_reuse[i]);
                        }
                }
                if(DEBUG_GEN) {
                        cout << "Number of unique MB reuse values = " << unique_MB_reuse.size() << endl;
                }
	}

	uint64_t is_mb_used(uint64_t mb_addr) {
		bool mb_found = false;
		uint64_t temporal_pos = 0;
		for (LMB_IT lit = last_macroblock_list.begin(); lit != last_macroblock_list.end(); lit++) {
			if(*lit == mb_addr) {
                                mb_found = true;
                                break;
                        }
			temporal_pos++;
		}
		if(mb_found == false)
                        temporal_pos = MAX_MB_REUSE;

		if(DEBUG_GEN) {
			cout << "In is_mb_used, mb_addr = " << mb_addr << ", mb_found = " << mb_found << ", temporal_pos = " << temporal_pos << endl;
		}

		if(!( ( (temporal_pos == MAX_MB_REUSE) && (mb_found == false) ) || ( (temporal_pos < MAX_MB_REUSE) && (mb_found == true) ) )) {	
			assert(0);
		}

		return temporal_pos;
	}

	void print_mb_reuse_list() {
                cout << "In print_mb_reuse_list, size = " << last_macroblock_list.size() << ", ";
                for (LMB_IT lit = last_macroblock_list.begin(); lit != last_macroblock_list.end(); lit++) {
                        cout << "MB# " << *lit << " = " << (per_MB_historytable[*lit])->get_num_accesses() << ", ";
                }
                cout << endl;
        }

	void update_mb_reuse_list(uint64_t mb_addr) {
                uint64_t temporal_pos = 0;
                bool mb_found = false;
                for (LMB_IT lit = last_macroblock_list.begin(); lit != last_macroblock_list.end(); lit++) {
                        if(*lit == mb_addr) {
                                last_macroblock_list.erase(lit);
                                mb_found = true;
                                break;
                        }
                        temporal_pos++;
                }

                if(last_macroblock_list.size() == MAX_MB_REUSE) {
                        last_macroblock_list.pop_back();
                }

                last_macroblock_list.push_front(mb_addr);
        }

	void check_addr_reuse(uint64_t mb_addr) {
		uint64_t temporal_pos = 0;
                bool mb_found = false;
                for (LMB_IT lit = last_macroblock_list.begin(); lit != last_macroblock_list.end(); lit++) {
                        if(*lit == mb_addr) {
                                last_macroblock_list.erase(lit);
                                mb_found = true;
                                break;
                        }
                        temporal_pos++;
                }

                if(last_macroblock_list.size() == MAX_MB_REUSE) {
                        last_macroblock_list.pop_back();
                }

                last_macroblock_list.push_front(mb_addr);

                if(mb_found == false)
                        temporal_pos = MAX_MB_REUSE;

		if(DEBUG) {
			cout << "Temporal reuse for md_addr " << mb_addr << " = " << temporal_pos << endl;
		}

                MB_reuse[temporal_pos] += 1;
        }

	void mem_access(uint64_t addr) {
		uint64_t this_mb = (addr >> MACROBLOCK_SIZE_BITS);
		mb_list.push_back(this_mb);

		if(DEBUG) {
			cout << "Num elems # " << num_elems << ", addr = " << addr << ", this_mb = " << this_mb << endl;
		}

		check_addr_reuse(this_mb);

		PMB_DIT mit = per_MB_historytable.find(this_mb);
		if(mit == per_MB_historytable.end()) {
			MACRO_BLOCK_LOC* mbl = new MACRO_BLOCK_LOC(addr, this_mb);
			per_MB_historytable[this_mb] = mbl;
			unique_mbs.push_back(this_mb);
		}
		else {
			mit->second->access_mb(addr);
		}
		if(init_addrs.size() <= MAX_INIT_ELEMS) {
                        init_addrs.push_back(addr);
                }

		/*
		cout << "Printing global delta table stats\n";
		for(GDT_IT git = global_delta_tables.begin(); git != global_delta_tables.end(); git++) {
                        git->second.print_tables();
                }
		*/
	}	

	bool get_next_delta(uint64_t temp_mb, uint64_t last_addr, uint64_t* temp_addr, int64_t* temp_delta) {
		bool addr_found = false;
		int num_trys = 0;
		uint64_t tA = 0;
		int64_t tD = 0;

		int64_t try_delta = 0;
		uint64_t try_addr = 0;

		if(DEBUG_GEN) {
			cout << "In get next delta for MB " << temp_mb << ", last_addr = " << last_addr << endl;
		}

		//Check if remaining elements in first N delta
		if((per_MB_historytable[temp_mb])->first_N_deltas.size() > 0) 
		{
			//if so, get delta from first N delta
			tD = (per_MB_historytable[temp_mb])->first_N_deltas.front();
			tA = last_addr + tD;
		
			if(DEBUG_GEN) {
				cout << "More deltas in First-N-Deltas, delta = " << tD << ", address = " << tA << endl;
			}

			assert((tA >> MACROBLOCK_SIZE_BITS) == temp_mb);
			addr_found = true;

			//Update delta tables
			(per_MB_historytable[temp_mb])->first_N_deltas.pop_front();
		}
		else {
			//If not, need to get delta from cascaded tables
			GDT_IT git;
			std::map<std::string, DELTA_ENTRY>::iterator ndit;
			std::string part_hash = "";

			if(DEBUG_GEN) {
				cout << "Need to get delta from cascaded tables, last_N_deltas.size() = " << (per_MB_historytable[temp_mb])->last_N_deltas.size() << endl;
			}

			//Check tables of history len from last_N_delta.size to 1 for delta match
			for(int i = (per_MB_historytable[temp_mb])->last_N_deltas.size(); i > 0; i--) {
				part_hash = (per_MB_historytable[temp_mb])->get_partial_delta_string(i);
				if(DEBUG_GEN) {
					
					cout << "Len = " << i << ", part hash of last deltas = " << part_hash << endl;
				}

				git = global_delta_tables.find(i);
        			if(git != global_delta_tables.end()) {	
					ndit = git->second.next_deltas.find(part_hash);

					if(ndit != git->second.next_deltas.end()) {
						if(DEBUG_GEN) {
							cout << "Matching hashed delta found in DELTA tables. Trying to get next delta, number of attempts = " << (ndit->second.get_num_followers() * 10) << "\n";
						}
						//When there is a match, get next delta

						//add next-delta to last address. 
						//if new address in the same page, delta found
						//else try again for max-try times.
						if(ndit->second.valid) {
							int max_trys = 0;
							while(max_trys < (ndit->second.get_num_followers() * 20)) {
								try_delta = ndit->second.get_rand_delta();	
								try_addr = last_addr + try_delta;
								if(DEBUG_GEN) {
									cout << "Delta attempt# " << max_trys << ", try_delta = " << try_delta << ", try_addr = " <<  try_addr << ", try_mb = " << (try_addr >> MACROBLOCK_SIZE_BITS) << ", this_mb = " << temp_mb << endl; 
								}
								if((try_addr >> MACROBLOCK_SIZE_BITS) == temp_mb) {
									addr_found = true;
									tA = try_addr;
									tD = try_delta;
									if(DEBUG_GEN) {
										cout << "Delta found " << tD << ", addr = " << tA << endl;
									}
									ndit->second.update_proxy(try_delta);
									break;
								}
								max_trys++;
							}
						}
					}
				}

				if(addr_found) {
					break;
				}
			}
		}
		if(DEBUG_GEN) {
			cout << "Addr found = " << addr_found << endl;
		}
		//If delta still not found, return false
		if(addr_found == false) {
			bool delt_fd = false;
			GDT_IT git;
                        std::map<std::string, DELTA_ENTRY>::iterator ndit;
                        std::string part_hash = "";

			if(DEBUG_GEN) {
				cout << "In get_next_delta, No address found in random attempts.\n";
			}
			for(int i = (per_MB_historytable[temp_mb])->last_N_deltas.size(); i > 0; i--) {
                                part_hash = (per_MB_historytable[temp_mb])->get_partial_delta_string(i);
                                if(DEBUG_GEN) {
                                        cout << "Forced Delta attempt: Len = " << i << ", part hash of last deltas = " << part_hash << endl;
                                }

                                git = global_delta_tables.find(i);
                                if(git != global_delta_tables.end()) {
                                        ndit = git->second.next_deltas.find(part_hash);

                                        if(ndit != git->second.next_deltas.end()) {
                                                if(DEBUG_GEN) {
                                                        cout << "Forced Delta attempt: Matching hashed delta found in DELTA tables. Trying to get next delta\n";
                                                }
						if(ndit->second.valid) {
                                                	try_delta = ndit->second.get_forced_delta(temp_mb, last_addr, &delt_fd);
							if(delt_fd) {
                                                        	try_addr = last_addr + try_delta;
                                                        	if(DEBUG_GEN) {
                                                             	cout << "Forced Delta attempt, try_delta = " << try_delta << ", try_addr = " <<  try_addr << ", try_delta_mb = " << (try_addr >> MACROBLOCK_SIZE_BITS) << ", this_mb = " << temp_mb << endl;
                                                        	}
                                                        	if((try_addr >> MACROBLOCK_SIZE_BITS) == temp_mb) {
                                                        		addr_found = true;
                                                                	tA = try_addr;
                                                                	tD = try_delta;
                                                                	if(DEBUG_GEN) {
                                                                		cout << "Forced Delta attempt: Delta found " << tD << ", addr = " << tA << endl;
                                                                	}
                                                                	ndit->second.update_proxy(try_delta);
								}
								else {
									assert(0);
								}
                                                        }
                                                }
                                        }
                                }

                                if(addr_found) {
                                        break;
                                }
                        }

			if(addr_found) {
				*temp_addr = tA;
                        	*temp_delta = tD;
                        	return true;
			}
			else {
				*temp_addr = 0;
				*temp_delta = 0;
				return false;
			}
		}
		else {
			*temp_addr = tA;
                        *temp_delta = tD;
			return true;
		}
	}

	bool reinit_MB_delta(uint64_t mb_addr) {
		bool reinit_MB_delta_first = false;
		if(DEBUG_GEN) {
                	cout << "In reinit_MB_delta for MB " << mb_addr << ", last_addr = " << (per_MB_historytable[mb_addr])->last_addr << endl;
		}

		bool reinit_found = false;
		bool val_delta_found = false;
		GDT_IT git;
		std::map<std::string, DELTA_ENTRY>::iterator ndit;
                std::string part_hash = "";

		int orig_len = (per_MB_historytable[mb_addr])->last_N_deltas.size();
		std::string orig_hash = (per_MB_historytable[mb_addr])->get_partial_delta_string(orig_len);
		uint64_t last_addr_mb = (per_MB_historytable[mb_addr])->last_addr;
		assert(mb_addr == (last_addr_mb >> MACROBLOCK_SIZE_BITS));

		if((per_MB_historytable[mb_addr])->first_N_deltas.size() > 0) {
			if(DEBUG_GEN) {
                        	cout << "This MB has still deltas left in first_N_deltas, size = " << (per_MB_historytable[mb_addr])->first_N_deltas.size() << ", so, no reiniting for it. last_N_delta len = " << orig_len << ", orig_hash = " << orig_hash << "\n";
			}
                        return false;
                }
		while(true)  {
			int curr_lastN_len = (per_MB_historytable[mb_addr])->last_N_deltas.size();
			assert(curr_lastN_len > 0);
			part_hash = (per_MB_historytable[mb_addr])->get_partial_delta_string(curr_lastN_len);
			if(DEBUG_GEN) {
				cout << "Top level, curr_lastN_len = " << curr_lastN_len << ", part hash = " << part_hash << endl;
			}

			for(int i = curr_lastN_len; i > 0; i--) {
                                part_hash = (per_MB_historytable[mb_addr])->get_partial_delta_string(i);
                                if(DEBUG_GEN) {
                                        cout << "Subpart of top level hash. Len = " << i << ", part hash of last deltas = " << part_hash << endl;
                                }
			
				git = global_delta_tables.find(i);
                        	if(git != global_delta_tables.end()) {
                        		ndit = git->second.next_deltas.find(part_hash);
					if(ndit != git->second.next_deltas.end()) {
						if(ndit->second.valid) {
							val_delta_found = ndit->second.is_any_delta_valid(last_addr_mb, mb_addr);
							if(val_delta_found) {
								reinit_found = true;
								break;
							}
						}
					}
				}
			}

			if(reinit_found) {
				if(DEBUG_GEN) {
					cout << "In reinit_MB_delta for MB " << mb_addr << ", orig last_N_delta len = " << orig_len << ", reinit delta found for new last_N_delta len = " << curr_lastN_len << ", part_hash = " << part_hash << endl;
				}
				break;
			}
			else {
				assert((per_MB_historytable[mb_addr])->last_N_deltas.size() > 0);
				(per_MB_historytable[mb_addr])->last_N_deltas.pop_back();

				if((per_MB_historytable[mb_addr])->last_N_deltas.size() == 0) {
					//Initialize to first addr and first N deltas for this MB
					if((per_MB_historytable[mb_addr])->reuse_first_addr() == true) {
						(per_MB_historytable[mb_addr])->reinit_first_addr();
						if(DEBUG_GEN) {
							cout << "Reiniting the access history of MB " << mb_addr << " to first addr\n";
						}
						reinit_MB_delta_first = true;
						break;
					}
					else {
						cout << "Could not find any shorter reuse path or first reuse for reinitialization of last N deltas. In reinit_MB_delta for MB " << mb_addr << ", orig last_N_delta len = " << orig_len << ", orig_hash = " << orig_hash << ", last_addr = " << last_addr_mb << endl;
						assert(0);
					}
				}
			}
		}
		return reinit_MB_delta_first;
	}

	void generate_proxy_access(unsigned phase_ct) {
        	//1. Get number of elements to generate
                uint64_t gen_elems = 0;
                int PROB_PICK_MB = 100;
                int TOT_MB_REUSE = 0;
                bool force_done = false;

                bool reuse_found = false;
                bool delta_found = false;

                uint64_t this_addr = 0;
                unsigned this_reuse = 0;
                int64_t this_delta = 0;
                uint64_t this_mb = 0;
                bool this_first_access = false;

                unsigned temp_reuse = 0;
                uint64_t temp_mb = 0;
                int num_max_reuse_trys = 0;
                uint64_t temp_addr = 0;
                int64_t temp_delta = 0;

                unsigned num_addr_trys = 0;
                int temp_new_page_prob = 0;
		bool reinit_MB_delta_first = false;

                for(int i = 0; i <= MAX_MB_REUSE; i++) {
                        TOT_MB_REUSE += MB_reuse[i];
                }

		std::vector<uint64_t> pgen_MB_reuse;
                pgen_MB_reuse.clear();
                pgen_MB_reuse.resize(MAX_MB_REUSE + 1);
                for(int i = 0; i <= MAX_MB_REUSE; i++) {
                        pgen_MB_reuse[i] = 0;
                }

                std::map <uint64_t, unsigned> new_MBs;
                new_MBs.clear();
                std::map<uint64_t, unsigned>::iterator NIT;

		if(DEBUG_GEN) {
                	cout << "\nIn generate proxy_access, num_elems = " << num_elems << ", phase_ct = " << phase_ct << endl;
		}

                std::vector<uint64_t> unique_MB_reuse_prob;
                unique_MB_reuse_prob.clear();
                uint64_t tot_rct = 0, runn_rct = 0;
                std::vector<uint64_t>::iterator umic;
                int klm = 0;
                bool klm_found = false;
                for(umic = unique_MB_reuse_ct.begin(); umic != unique_MB_reuse_ct.end(); umic++) {
                        tot_rct += (*umic);
                }
		if(DEBUG_GEN) {
                	cout << "Unique MB reuse probability: ";
		}
                for(umic = unique_MB_reuse_ct.begin(); umic != unique_MB_reuse_ct.end(); umic++) {
                        runn_rct += (*umic);
                        unique_MB_reuse_prob.push_back((runn_rct * 100)/tot_rct);
			if(DEBUG_GEN) {
                        	cout << unique_MB_reuse[klm] << " = " << unique_MB_reuse_prob[klm] << ", ";
			}
                        klm++;
                }
		if(DEBUG_GEN) {
                	cout << endl;
		}
                std::vector<uint64_t> unique_MB_prob;
                unique_MB_prob.clear();
                tot_rct = 0;
                runn_rct = 0;
                klm = 0;
                klm_found = false;
                for(umic = unique_mb_ct.begin(); umic != unique_mb_ct.end(); umic++) {
                        tot_rct += (*umic);
                }
		if(DEBUG_GEN) {
                	cout << "Unique MB probability: ";
		}
                for(umic = unique_mb_ct.begin(); umic != unique_mb_ct.end(); umic++) {
                        runn_rct += (*umic);
                        unique_MB_prob.push_back((runn_rct * 100)/tot_rct);
			if(DEBUG_GEN) {
                        	cout << unique_mbs[klm] << " = " << unique_MB_prob[klm] << ", ";
			}
                        klm++;
                }
		if(DEBUG_GEN) {
               		cout << endl;
		}

                unsigned case_num = 0;
		//2. for each element to generate
                while(gen_elems < (PHASE_LEN / 5)) { //num_elems) {
                        if(DEBUG_GEN) {
                                cout << "\nMJ: In proxy gen, gen_elems = " << gen_elems << ", TOT_MB_REUSE = " << TOT_MB_REUSE << endl;
                        }
                        case_num = 0;

                        this_reuse = 0;
                        this_addr = 0;
                        this_delta = 0;
                        this_mb = 0;
                        reuse_found = false;
                        delta_found = false;
                        this_first_access = false;

                        num_addr_trys = 0;
                        temp_new_page_prob = 0;
                        temp_addr = 0;
                        temp_delta = 0;
			reinit_MB_delta_first = false;

			if(gen_elems <= MAX_INIT_ELEMS) {
                                assert(init_addrs.size() > 0);
                                this_addr = init_addrs.front();
                                this_mb = this_addr >> MACROBLOCK_SIZE_BITS;
                                this_first_access = (per_MB_historytable[this_mb])->is_first_access();
                                if(this_first_access) {
                                        this_delta = 0;
                                }
                                else {
                                        this_delta = (per_MB_historytable[this_mb])->get_delta(this_addr);
                                        if((per_MB_historytable[this_mb])->first_N_deltas.size() > 0) {
                                                assert(this_delta == (per_MB_historytable[this_mb])->first_N_deltas.front());
                                                (per_MB_historytable[this_mb])->first_N_deltas.pop_front();
                                        }
                                }
                                this_reuse = is_mb_used(this_mb);
                                reuse_found = true;

                                init_addrs.pop_front();
                                case_num = 1;
                        }

			while(reuse_found == false) {
                                //3. Get a reuse distance value
                                PROB_PICK_MB = rand() % 100;
                                klm = 0;
                                klm_found = false;
                                for(umic = unique_MB_reuse_prob.begin(); umic != unique_MB_reuse_prob.end(); umic++) {
                                        if(PROB_PICK_MB <= (*umic)) {
                                                temp_reuse = unique_MB_reuse[klm];
                                                klm_found = true;
                                                break;
                                        }
                                        klm++;
                                }
                                assert(klm_found == true);

                                //4. If max reuse distance, get a new page from the unique list
                                //if((temp_new_page_prob < PROB_PICK_NEW_MB) && (temp_reuse == MAX_MB_REUSE) && (MB_reuse[temp_reuse] > 0)) {
				if((temp_reuse == MAX_MB_REUSE) && (MB_reuse[temp_reuse] > 0)) {
                                        if(DEBUG_GEN) {
                                                cout << "Max reuse picked, trying to get a new page address\n";
                                        }
                                        num_max_reuse_trys = 1000;
                                        while(num_max_reuse_trys > 0) {

                                                PROB_PICK_MB = rand() % 100;
                                                klm = 0;
                                                klm_found = false;
                                                for(umic = unique_MB_prob.begin(); umic != unique_MB_prob.end(); umic++) {
                                                        if(PROB_PICK_MB <= (*umic)) {
                                                                temp_mb = unique_mbs[klm];
                                                                klm_found = true;
                                                                break;
                                                        }
                                                        klm++;
                                                }
                                                assert(klm_found == true);

                                                NIT = new_MBs.find(temp_mb);
						if((is_mb_used(temp_mb) == MAX_MB_REUSE) && (NIT == new_MBs.end()) && ((per_MB_historytable[temp_mb])->get_num_accesses() > 0)) {
                                                        this_reuse = MAX_MB_REUSE;
                                                        this_first_access = (per_MB_historytable[temp_mb])->is_first_access();
                                                        assert(this_first_access == true);
                                                        this_addr = (per_MB_historytable[temp_mb])->get_first_address();
                                                        this_delta = 0;
                                                        this_mb = temp_mb;
                                                        reuse_found = true;
                                                        if(DEBUG_GEN) {
                                                                cout << "MJ: In Proxy gen, Max reuse found, Picking new MB. this_addr = " << this_addr << ", this_first_access = " << this_first_access << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                        }
                                                        case_num = 2;
                                                        break;
                                                }
                                                else if((is_mb_used(temp_mb) == MAX_MB_REUSE) && (NIT != new_MBs.end()) && ((per_MB_historytable[temp_mb])->get_num_accesses() > 0)) {
                                                        delta_found = get_next_delta(temp_mb, (per_MB_historytable[temp_mb])->last_addr, &temp_addr, &temp_delta);
                                                        if(delta_found) {
                                                                this_reuse = MAX_MB_REUSE;
                                                                this_addr = temp_addr;
                                                                this_delta = temp_delta;
                                                                this_mb = temp_mb;
                                                                reuse_found = true;
                                                                if(DEBUG_GEN) {
                                                                        cout << "MJ: In max_reuse, but MB seen before. Delta found, this_reuse = " << this_reuse << ", this_addr = " << this_addr << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                                }
                                                                case_num = 3;
                                                                break;
                                                        }//TBD-Add reinit
							else {
								if(DEBUG_GEN) {
									cout << "Why MB " << temp_mb << " has no valid delta. Trying re-init. Going back to first address.\n";
								}
								reinit_MB_delta_first = reinit_MB_delta(temp_mb);
								if(reinit_MB_delta_first) {
									this_first_access = true;
									this_reuse = MAX_MB_REUSE;
									this_addr = (per_MB_historytable[temp_mb])->get_first_address();
									this_delta = 0;
									this_mb = temp_mb;
									reuse_found = true;
									break;
								}
								//assert(0);
							}
        	                                }
						num_max_reuse_trys--;
                                        }
                                        if(reuse_found == false) {
                                                if(DEBUG_GEN) {
                                                        cout << "Could not get a new page to assign. Trying another reuse\n";
                                                }
                                        }
                                }
				else if((temp_reuse < MAX_MB_REUSE) && (temp_reuse < last_macroblock_list.size()) && (MB_reuse[temp_reuse] > 0)) {
                                        //temp_mb = last_macroblock_list[last_macroblock_list.size() - temp_reuse - 1];
                                        int temporal_pos = 0;
                                        for (LMB_IT lit = last_macroblock_list.begin(); lit != last_macroblock_list.end(); lit++) {
                                                if(temporal_pos == temp_reuse) {
                                                        temp_mb = *lit;
                                                        break;
                                                }
                                                temporal_pos++;
                                        }

                                        if(DEBUG_GEN) {
                                                cout << "Lower reuse tried = " << temp_reuse << ", less than last_macroblock_list.size() = " << last_macroblock_list.size() << ", temp_mb = " << temp_mb << endl;
                                        }

                                        if((per_MB_historytable[temp_mb])->get_num_accesses() > 0) {
                                                delta_found = get_next_delta(temp_mb, (per_MB_historytable[temp_mb])->last_addr, &temp_addr, &temp_delta);

                                                //5. If reuse page exists, access the last delta table to get last N deltas
                                                //5a. If last delta size = 0, get the new page first delta value
                                                //5b. If not, get a delta from the cascaded tables, such that the new address does not cross the page boundary
                                                if(delta_found) {
                                                        this_reuse = temp_reuse;
                                                        this_addr = temp_addr;
                                                        this_delta = temp_delta;
                                                        this_mb = temp_mb;
                                                        reuse_found = true;
                                                        if(DEBUG_GEN) {
                                                                cout << "Delta found for lower reuse = " << this_reuse << ", this_addr = " << this_addr << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                        }
                                                        case_num = 4;
                                                }
                                                else { //TBD-Add reinit
                                                        if(DEBUG_GEN) {
                                                                cout << "No such lower reuse delta follower found\n";
                                                                cout << "Why MB " << temp_mb << " has no valid delta. Trying re-init. Going back to first address.\n";
                                                        }
                                                        reinit_MB_delta_first = reinit_MB_delta(temp_mb);
							if(reinit_MB_delta_first) {
                                                                this_first_access = true;
                                                                this_reuse = temp_reuse;
                                                                this_addr = (per_MB_historytable[temp_mb])->get_first_address();
                                                                this_delta = 0;
                                                                this_mb = temp_mb;
                                                                reuse_found = true;
                                                                break;
                                                                //assert(0);
                                                        }
                                                }
                                        }
                                        else {
                                                if(DEBUG_GEN) {
                                                        cout << "This lower reuse page has no more accesses left\n";
                                                }
                                        }
				}
                                else if((temp_reuse < MAX_MB_REUSE) && (temp_reuse >= last_macroblock_list.size()) && (MB_reuse[temp_reuse] > 0)) {
                                        if(DEBUG_GEN) {
                                                cout << "MJ: Lower reuse picked = " << temp_reuse << ", more than/equal to last_macroblock_list.size() = " << last_macroblock_list.size() << ", trying to pick new MB to fill the last_macroblock list " << endl;
                                        }
                                        num_max_reuse_trys = 500;
                                        while(num_max_reuse_trys > 0) {
                                                PROB_PICK_MB = rand() % 100;
                                                klm = 0;
                                                klm_found = false;
                                                for(umic = unique_MB_prob.begin(); umic != unique_MB_prob.end(); umic++) {
                                                        if(PROB_PICK_MB <= (*umic)) {
                                                                temp_mb = unique_mbs[klm];
                                                                klm_found = true;
                                                                break;
                                                        }
                                                        klm++;
                                                }
                                                assert(klm_found == true);

                                                //temp_mb =  unique_mbs[rand() % per_MB_historytable.size()];
                                                NIT = new_MBs.find(temp_mb);
						if((is_mb_used(temp_mb) == MAX_MB_REUSE) && (NIT == new_MBs.end()) && ((per_MB_historytable[temp_mb])->get_num_accesses() > 0)) {
                                                        this_reuse = MAX_MB_REUSE;
                                                        this_first_access = (per_MB_historytable[temp_mb])->is_first_access();
                                                        assert(this_first_access == true);
                                                        this_addr = (per_MB_historytable[temp_mb])->get_first_address();
                                                        this_delta = 0;
                                                        this_mb = temp_mb;
                                                        reuse_found = true;
                                                        if(DEBUG_GEN) {
                                                                cout << "MJ: In Proxy gen, Trying to increase size of last macroblock list by Picking new MB. this_addr = " << this_addr << ", this_first_access = " << this_first_access << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                        }
                                                        case_num = 5;
                                                        break;
                                                }
                                                else if((is_mb_used(temp_mb) == MAX_MB_REUSE) && (NIT != new_MBs.end()) && ((per_MB_historytable[temp_mb])->get_num_accesses() > 0)) {
                                                        delta_found = get_next_delta(temp_mb, (per_MB_historytable[temp_mb])->last_addr, &temp_addr, &temp_delta);
                                                        if(delta_found) {
                                                                this_reuse = MAX_MB_REUSE;
                                                                this_addr = temp_addr;
                                                                this_delta = temp_delta;
                                                                this_mb = temp_mb;
                                                                reuse_found = true;
                                                                if(DEBUG_GEN) {
                                                                        cout << "MJ: In max_reuse, but MB seen before. Delta found, this_reuse = " << this_reuse << ", this_addr = " << this_addr << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                                }
                                                                case_num = 6;
                                                                break;
                                                        }
							else { //TBD-Add reinit
                                                        	if(DEBUG_GEN) {
									cout << "MB " << temp_mb << " has no valid delta. Trying re-init.\n";
								}
								reinit_MB_delta_first = reinit_MB_delta(temp_mb);
								if(reinit_MB_delta_first) {
									this_first_access = true;
									this_reuse = MAX_MB_REUSE;
									this_addr = (per_MB_historytable[temp_mb])->get_first_address();
									this_delta = 0;
									this_mb = temp_mb;
                                                                	reuse_found = true;
                                                                	break;
                                                        	}
                                                	}
                                                }
                                                num_max_reuse_trys--;
                                        }
                                        if(reuse_found == false) {
                                                if(DEBUG_GEN) {
                                                        cout << "Could not get a new page to increase the macroblock list size. Trying another reuse\n";
                                                }
                                        }
                                }
                                else {
                                        //Do nothing
                                }
                                num_addr_trys++;
                                bool mb_found_fin = false;

                                int max_nonzero_reuse = 0;
                                bool max_nonzero_reuse_found = false;
                                if((num_addr_trys == 1) && (reuse_found == false)) {
                                        for(std::vector<unsigned>::iterator umrit = unique_MB_reuse.begin(); umrit != unique_MB_reuse.end(); umrit++) {
                                                if((*umrit != MAX_MB_REUSE) && (*umrit >= max_nonzero_reuse) && (MB_reuse[*umrit] > 0)) {
                                                        max_nonzero_reuse = *umrit;
                                                        max_nonzero_reuse_found = true;
                                                }
                                        }
                                        if(DEBUG_GEN) {
                                                cout << "MJ: MAX address tries exhausted. max_nonzero_reuse = " << max_nonzero_reuse << ", last_macroblock_list.size = " << last_macroblock_list.size() << endl;
                                        }
                                        if((max_nonzero_reuse_found == true) && (max_nonzero_reuse >= last_macroblock_list.size())) {
                                                num_max_reuse_trys = 500;
                                                while(num_max_reuse_trys > 0) {
                                                        PROB_PICK_MB = rand() % 100;
                                                        klm = 0;
                                                        klm_found = false;
                                                        for(umic = unique_MB_prob.begin(); umic != unique_MB_prob.end(); umic++) {
                                                                if(PROB_PICK_MB <= (*umic)) {
                                                                        temp_mb = unique_mbs[klm];
                                                                        klm_found = true;
                                                                        break;
                                                                }
                                                                klm++;
                                                        }
                                                        assert(klm_found == true);

                                                        //temp_mb =  unique_mbs[rand() % per_MB_historytable.size()];
                                                        NIT = new_MBs.find(temp_mb);
							if((is_mb_used(temp_mb) == MAX_MB_REUSE) && (NIT == new_MBs.end()) && ((per_MB_historytable[temp_mb])->get_num_accesses() > 0)) {
                                                                this_reuse = MAX_MB_REUSE;
                                                                this_first_access = (per_MB_historytable[temp_mb])->is_first_access();
                                                                assert(this_first_access == true);
                                                                this_addr = (per_MB_historytable[temp_mb])->get_first_address();
                                                                this_delta = 0;
                                                                this_mb = temp_mb;
                                                                reuse_found = true;
                                                                if(DEBUG_GEN) {
                                                                        cout << "MJ: MAX_TRY #1. MAX non zero reuse is larger than last macroblock size. Picking new MB, this_addr = " << this_addr << ", this_first_access = " << this_first_access << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                                }
                                                                case_num = 7;
                                                                break;
                                                        }
                                                        num_max_reuse_trys--;
                                                }
                                        }
					else if((max_nonzero_reuse_found == true) && (max_nonzero_reuse < last_macroblock_list.size())) {
                                                int temporal_pos = 0;
                                                bool max_nonzero_reuse_zeroval = false;
                                                uint64_t trial_mb;
                                                unsigned trial_reuse_val = 0;
                                                bool higher_reuse_found = false;
                                                temp_addr = 0;
                                                temp_delta = 0;

                                                for (LMB_IT lit = last_macroblock_list.begin(); lit != last_macroblock_list.end(); lit++) {
                                                        trial_mb = *lit;
                                                        if(temporal_pos == max_nonzero_reuse) {
                                                                if((per_MB_historytable[trial_mb])->get_num_accesses() == 0) {
                                                                        max_nonzero_reuse_zeroval = true;
                                                                }
								temp_mb = trial_mb;
                                                                trial_reuse_val = temporal_pos;
                                                        }
                                                        if(max_nonzero_reuse_zeroval && ((per_MB_historytable[trial_mb])->get_num_accesses() > 0)) {
                                                                temp_mb = trial_mb;
                                                                trial_reuse_val = temporal_pos;
                                                                higher_reuse_found = true;
                                                        }
                                                        temporal_pos++;
                                                }

                                                if(DEBUG_GEN) {
                                                        cout << "MJ: MAX address tries exhausted. Higher reuse elements present? " << higher_reuse_found << " (reuse_val = " << trial_reuse_val << ", reuse mb = " << temp_mb << ", on the list than what max reuse value " << max_nonzero_reuse << " permits.\n";
                                                }
                                                if(higher_reuse_found) {
                                                        assert((per_MB_historytable[temp_mb])->get_num_accesses() > 0);
                                                }
                                                if(higher_reuse_found && ((per_MB_historytable[temp_mb])->get_num_accesses() > 0)) {
                                                        delta_found = get_next_delta(temp_mb, (per_MB_historytable[temp_mb])->last_addr, &temp_addr, &temp_delta);
                                                        if(delta_found) {
                                                                this_reuse = trial_reuse_val;
                                                                this_addr = temp_addr;
                                                                this_delta = temp_delta;
                                                                this_mb = temp_mb;
                                                                reuse_found = true;
                                                                if(DEBUG_GEN) {
                                                                        cout << "MJ MAX_TRY #2: MAX address gen tries exhausted. Found possible HIGHER reuse within max last macroblock list size. Delta found, this_reuse = " << this_reuse << ", this_addr = " << this_addr << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                                }
                                                                case_num = 8;
                                                        }
							else { //TBD-Add reinit
                                                                if(DEBUG_GEN) {
                                                                        cout << "MB " << temp_mb << " has no valid delta. Trying re-init.\n";
                                                                }
                                                                reinit_MB_delta_first = reinit_MB_delta(temp_mb);
                                                                if(reinit_MB_delta_first) {
                                                                        this_first_access = true;
                                                                        this_reuse = trial_reuse_val;
                                                                        this_addr = (per_MB_historytable[temp_mb])->get_first_address();
                                                                        this_delta = 0;
                                                                        this_mb = temp_mb;
                                                                        reuse_found = true;
                                                                        break;
                                                                }
								else {
									this_first_access = true;
	                                                                this_reuse = temp_reuse;
        	                                                        this_addr = (per_MB_historytable[temp_mb])->last_addr;
                	                                                this_delta = 0;
                        	                                        this_mb = temp_mb;
                                	                                reuse_found = true;
                                        	                        break;
								}
                                                        }
                                                }
                                                else if(higher_reuse_found) {
                                                        cout << "Not possible case\n";
                                                        print_reuse_info();
                                                        assert(0);
                                                }
                                        }
                                        /*
                                        if(reuse_found == false) {
                                                temp_addr = 0;
                                                temp_delta = 0;
                                                //MAX-TRY2: Trying to get possible reuse within max last macroblock list size
                                                for(int ijk = (last_macroblock_list.size() - 1); ijk >= 0; ijk--) {
                                                        int temporal_pos = 0;
                                                        mb_found_fin = false;
                                                        for (LMB_IT lit = last_macroblock_list.begin(); lit != last_macroblock_list.end(); lit++) {
                                                                if(temporal_pos == ijk) {
                                                                        temp_mb = *lit;
                                                                        temp_reuse = ijk;
                                                                        mb_found_fin = true;
                                                                        break;
                                                                }
                                                                temporal_pos++;
                                                        }
                                                        assert(mb_found_fin == true);
                                                        if(((per_MB_historytable[temp_mb])->get_num_accesses() > 0) && (MB_reuse[temp_reuse] > 0)) {
                                                                delta_found = get_next_delta(temp_mb, (per_MB_historytable[temp_mb])->last_addr, &temp_addr, &temp_delta);
								if(delta_found) {
                                                                        this_reuse = temp_reuse;
                                                                        this_addr = temp_addr;
                                                                        this_delta = temp_delta;
                                                                        this_mb = temp_mb;
                                                                        reuse_found = true;
                                                                        if(DEBUG_GEN) {
                                                                                cout << "MJ MAX_TRY #3: MAX address gen tries exhausted. Found possible reuse within max last macroblock list size. Delta found, this_reuse = " << this_reuse << ", this_addr = " << this_addr << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                                        }
                                                                        case_num = 9;
                                                                        break;
                                                                }
                                                        }
                                                }
                                        }
                                        */
                                        if((reuse_found == false) && (MB_reuse[MAX_MB_REUSE] > 0)) {
                                                if(DEBUG_GEN) {
                                                        cout << "MJ: MAX_TRY #3: MAX address tries exhausted. No smaller reuse found. Trying max reuse to get new MB address\n";
                                                }
                                                num_max_reuse_trys = 10000;
                                                while(num_max_reuse_trys > 0) {
                                                        /*PROB_PICK_MB = rand() % 100;
                                                        klm = 0;
                                                        klm_found = false;
                                                        for(umic = unique_MB_prob.begin(); umic != unique_MB_prob.end(); umic++) {
                                                                if(PROB_PICK_MB <= (*umic)) {
                                                                        temp_mb = unique_mbs[klm];
                                                                        klm_found = true;
                                                                        break;
                                                                }
                                                                klm++;
                                                        }
                                                        assert(klm_found == true);
                                                        */
                                                        temp_mb = unique_mbs[rand() % per_MB_historytable.size()];
                                                        if((is_mb_used(temp_mb) == MAX_MB_REUSE) && ((per_MB_historytable[temp_mb])->get_num_accesses() > 0)) {
                                                                this_reuse = MAX_MB_REUSE;
                                                                this_addr = (per_MB_historytable[temp_mb])->get_first_address();
                                                                this_first_access = true;
                                                                this_delta = 0;
                                                                this_mb = temp_mb;
                                                                reuse_found = true;
                                                                if(DEBUG_GEN) {
                                                                        cout << "MJ: In Proxy gen, Max reuse picked by force, this_addr = " << this_addr << ", this_first_access = " << this_first_access << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                                }
                                                                case_num = 9;
                                                                break;
                                                        }
                                                        num_max_reuse_trys--;
                                                }
                                                if(reuse_found == false) {
                                                        cout << "Could not get a new page to assign even though MB_reuse[max_reuse] > 0. asserting for now\n";
                                                        print_reuse_info();
                                                        assert(0);
                                                }
                                        }
					if(reuse_found == false) {
                                                temp_addr = 0;
                                                temp_delta = 0;
                                                //MAX-TRY2: Trying to get possible reuse within max last macroblock list size
                                                for(int ijk = (last_macroblock_list.size() - 1); ijk >= 0; ijk--) {
                                                        int temporal_pos = 0;
                                                        mb_found_fin = false;
                                                        for (LMB_IT lit = last_macroblock_list.begin(); lit != last_macroblock_list.end(); lit++) {
                                                                if(temporal_pos == ijk) {
                                                                        temp_mb = *lit;
                                                                        temp_reuse = ijk;
                                                                        mb_found_fin = true;
                                                                        break;
                                                                }
                                                                temporal_pos++;
                                                        }
                                                        assert(mb_found_fin == true);
                                                        if(((per_MB_historytable[temp_mb])->get_num_accesses() > 0) && (MB_reuse[temp_reuse] > 0)) {
                                                                delta_found = get_next_delta(temp_mb, (per_MB_historytable[temp_mb])->last_addr, &temp_addr, &temp_delta);
                                                                if(delta_found) {
                                                                        this_reuse = temp_reuse;
                                                                        this_addr = temp_addr;
                                                                        this_delta = temp_delta;
                                                                        this_mb = temp_mb;
                                                                        reuse_found = true;
                                                                        if(DEBUG_GEN) {
                                                                                cout << "MJ MAX_TRY #4: MAX address gen tries exhausted. Found possible reuse within max last macroblock list size. Delta found, this_reuse = " << this_reuse << ", this_addr = " << this_addr << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                                        }//TBD-Add reinit
                                                                        case_num = 10;
                                                                        break;
                                                                }
								
                                                        }
                                                }
                                        }
                                        if(reuse_found == false) {
                                                for(NIT = new_MBs.begin(); NIT != new_MBs.end(); NIT++) {
							temp_mb = NIT->first;
                                                        if((per_MB_historytable[NIT->first])->get_num_accesses() > 0) {
                                                                delta_found = get_next_delta(NIT->first, (per_MB_historytable[NIT->first])->last_addr, &temp_addr, &temp_delta);
                                                                if(delta_found) {
                                                                        this_reuse = is_mb_used(NIT->first);
                                                                        this_addr = temp_addr;
                                                                        this_delta = temp_delta;
                                                                        this_mb = NIT->first;
                                                                        reuse_found = true;
                                                                        if(DEBUG_GEN) {
                                                                                cout << "MJ: MAX_TRY #5. Max address tries exhausted, no shorter reuse, no MAX reuse found. Found an MB with remaining accesses. Delta found, this_reuse = " << this_reuse << ", this_addr = " << this_addr << ", this_delta = " << this_delta << ", this_mb = " << this_mb << endl;
                                                                        }
                                                                        case_num = 11;
                                                                        break;
                                                                }
								else { //TBD-Add reinit
									if(DEBUG_GEN) {
										cout << "MB " << temp_mb << " has no valid delta. Trying re-init.\n";
									}
									reinit_MB_delta_first = reinit_MB_delta(temp_mb);
									if(reinit_MB_delta_first) {
										this_first_access = true;
										this_reuse = is_mb_used(temp_mb);
										this_addr = (per_MB_historytable[temp_mb])->get_first_address();
										this_delta = 0;
										this_mb = temp_mb;
										reuse_found = true;
										break;
									}
									else {
										this_first_access = true;
										this_reuse = is_mb_used(temp_mb);
										this_addr = (per_MB_historytable[temp_mb])->last_addr;
										this_delta = 0;
										this_mb = temp_mb;
										reuse_found = true;
										break;
									}
                                                        	}
                                                        }
                                                }
                                        }

                                        if (reuse_found == false) {
                                                if(gen_elems < ((95 * (PHASE_LEN - 10)/100))) {
                                                        cout << "How is it possible?\n";
                                                        print_reuse_info();
                                                        assert(0);
                                                }
                                                else {
                                                        force_done = true;
                                                }
                                                break;
                                        }
                                }
                        }
                        if(force_done) {
                                //break early
                                break;
                        }

                        if(DEBUG_GEN) {
                                cout << "Address GEN CASE " << case_num << endl;
                        }

                        assert(reuse_found == true);
                        //6. Assign address to the proxy entry, update the page last delta table.
                        cout << this_mb << ", " << this_addr << "," << this_reuse << "," << this_delta << endl;

                        //Update MB tables
                        (per_MB_historytable[this_mb])->proxy_access(this_delta, this_first_access, this_addr);
                        update_mb_reuse_list(this_mb);
                        assert((this_reuse >= 0) && (this_reuse <= MAX_MB_REUSE));

                        pgen_MB_reuse[this_reuse] += 1;

                        if(MB_reuse[this_reuse] > 0) {
                                MB_reuse[this_reuse] -= 1;
                        }

                        NIT = new_MBs.find(this_mb);
                        if(NIT == new_MBs.end()) {
                                new_MBs[this_mb] = 1;
                                assert(this_reuse == MAX_MB_REUSE);
                        }
                        else {
                                NIT->second += 1;
                                if((per_MB_historytable[this_mb])->last_N_deltas.size() != 0) {
                                        reinit_MB_delta(NIT->first);
                                }

                                if(this_reuse > MAX_MB_REUSE) {
					cout << "Asserting: This reuse = " << this_reuse << endl;
					assert(0);
				}
                        }

                        if(TOT_MB_REUSE == 0) {
                                TOT_MB_REUSE = 1;
                        }
                        else {
                                TOT_MB_REUSE--;
                        }

                        if(DEBUG_GEN) {
                                cout << "Num accesses left for this MB " << this_mb << " = " << (per_MB_historytable[this_mb])->get_num_accesses() << ", Num of new pages left per MB_reuse = " << MB_reuse[MAX_MB_REUSE] << ", num new pages generated = " << new_MBs.size() << ", last_macroblock_list.size = " << last_macroblock_list.size() << endl;
                        }

                        unique_MB_reuse_prob.clear();
                        tot_rct = 0, runn_rct = 0;
                        klm = 0;
                        klm_found = false;

                        for(umic = unique_MB_reuse_ct.begin(); umic != unique_MB_reuse_ct.end(); umic++) {
                                tot_rct += (*umic);
                                if(unique_MB_reuse[klm] == this_reuse) {
                                        if(*umic > 0) {
                                                *umic = *umic - 1;
                                                klm_found = true;
                                        }
                                }
                                klm++;
                        }

                        if(klm_found) {
                                tot_rct--;
                        }

                        if(tot_rct == 0) {
                                assert(0);
                        }

                        klm = 0;
                        klm_found = false;

                        if(DEBUG_GEN) {
                                cout << "Unique MB reuse probability: ";
                        }
                        for(umic = unique_MB_reuse_ct.begin(); umic != unique_MB_reuse_ct.end(); umic++) {
                                runn_rct += (*umic);
                                unique_MB_reuse_prob.push_back((runn_rct * 100)/tot_rct);
                                if(DEBUG_GEN) {
                                        cout << unique_MB_reuse[klm] << " = " << unique_MB_reuse_prob[klm] << ", ";
                                }
                                klm++;
                        }
                        if(DEBUG_GEN) {
                                cout << endl;
                        }

                        unique_MB_prob.clear();
                        tot_rct = 0, runn_rct = 0, klm = 0;
                        klm_found = false;
                        for(umic = unique_mb_ct.begin(); umic != unique_mb_ct.end(); umic++) {
                                tot_rct += (*umic);
                                if(unique_mbs[klm] == this_mb) {
                                        if(*umic > 0) {
                                                *umic = *umic - 1;
                                                klm_found = true;
                                        }
                                }
                                klm++;
                        }

                        if(klm_found) {
                                tot_rct--;
                        }

                        if(tot_rct == 0) {
                                assert(0);
                        }

                        klm = 0;
                        klm_found = false;

                        if(DEBUG_GEN) {
                                cout << "Unique MB probability: ";
                        }
                        for(umic = unique_mb_ct.begin(); umic != unique_mb_ct.end(); umic++) {
                                runn_rct += (*umic);
                                unique_MB_prob.push_back((runn_rct * 100)/tot_rct);
                                if(DEBUG_GEN) {
                                        cout << unique_mbs[klm] << " = " << unique_MB_prob[klm] << ", ";
                                }
                                klm++;
                        }
			if(DEBUG_GEN) {
                                cout << endl;
                        }

                        if(DEBUG_GEN) {
                                print_mb_reuse_list();
                                print_reuse_info();
                        }
                        gen_elems++;
                }
		if(DEBUG_GEN) {
                	cout << "Proxy Gen reuse info: ";
                	for(int pop = 0; pop <= MAX_MB_REUSE; pop++) {
                        	if(pgen_MB_reuse[pop] > 0) {
                                	cout << "[" << pop << "] = " << pgen_MB_reuse[pop] << ", ";
                        	}
                	}
                	cout << endl;
		}
	}

};

int main(int argc, char*  argv[]) {
    /////////////////////////
    //     parameters      //
    /////////////////////////
    uint64_t pc;
    uint64_t addr;
    unsigned iid;
    unsigned rw;

    size_t pos0;
    size_t pos1;
    size_t pos2;

    //std::cout <<"before opening file\n";
    // open file
    ifstream tfile;
    tfile.open (argv[1]);

    std::ofstream ofs;
    ofs.open (argv[2], std::ofstream::out);

    std::streambuf *buf;
    buf = ofs.rdbuf();
    //std::ostream out(buf);

    LOCALITY_MJ* lmj = new LOCALITY_MJ();

    lmj->set_streambuf(buf);
    srand (time(NULL));
   
    unsigned phase_ct = 0; 
    // main loop
    while(!tfile.eof()){
	string buffer;
	getline(tfile, buffer); 
	if(!tfile.eof()) {
	    //// EXTRACTING INFORMATION ////
	    //4202512,140623034683072, 2, 1
	    pos0  = buffer.find(",");
	    pos1  = buffer.find(",", pos0+1);
	    pos2  = buffer.find(",", pos1+1);

	    stringstream field1(buffer.substr(0, pos0));
            stringstream field2(buffer.substr(pos0+1, pos1-1));
            stringstream field3(buffer.substr(pos1+2, pos2-1));
            stringstream field4(buffer.substr(pos2+2, buffer.length()-pos2+1));

            field1 >> dec >> pc;
            field2 >> dec >> addr;
            field3 >> dec >> iid;
	    field4 >> dec >> rw;

	    if(DEBUG) {
	    	std::cout << "\n" << "Elem# " << num_elems << ": " << pc << ", " << addr << ", iid = " << iid << ", rw = " << rw << std::endl;
	    }

	    num_elems += 1;

	    lmj->mem_access(addr);		

	    if(((num_elems % PHASE_LEN) == 0) && (num_elems != 0)) {
			lmj->print_locality_info(phase_ct);
			lmj->prep4proxygen();
			lmj->generate_proxy_access(phase_ct);
			//lmj->print_reuse_info();
			lmj->phase_clear();
			phase_ct++;
	    }
	    /*if((num_elems % 20000000) == 0) {
		std::cout << "\n" << "Elem# " << num_elems << ": " << pc << ", " << addr << ", iid = " << iid << ", rw = " << rw << std::endl;
		break;
	    }*/
	}
    }
    std::cerr << "Num elems found = " << num_elems << endl;
    //lmj->print_locality_info();

    //Proxy Generation prepare - Clears last address list for individual PCs.
    //lmj->prep4proxygen();

    //Generate Proxy
    //lmj->generate_proxy_access();    

    tfile.close();
    ofs.close();
    return 0;
}
