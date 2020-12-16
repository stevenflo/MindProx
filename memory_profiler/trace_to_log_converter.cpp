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


//Modifying to 5 to allow space for the overflow regions
#define NUM_REG 5

#define NUM_MB_BITS 12

using namespace std;

unsigned long long num_elems = 0;
bool HALO = true;
bool DEBUG = false;
bool DEBUG_GEN = false; //true;

bool sortByVal(const pair<uint64_t, int> &a, 
               const pair<uint64_t, int> &b) 
{ 
  return (a.second > b.second); 
} 


vector<uint64_t> get_region_counts(char file[]){
  uint64_t mb;
  uint64_t addr;
  int64_t reuse;
  uint64_t offset;
  uint64_t count = 0;
  size_t pos0;
  size_t pos1;
  size_t pos2;
  ifstream tfile(file);
  map<uint64_t, int> mb_counts;
  //tfile.open (file);
  string buffer;
  while(!tfile.eof()){
    getline(tfile, buffer); 
    if(!tfile.eof()) {
      //// EXTRACTING INFORMATION ////
      //4202512,140623034683072, 2, 1
      //std::cout << buffer << endl;

      pos0  = buffer.find(",");
      pos1  = buffer.find(",", pos0+1);
      pos2  = buffer.find(",", pos1+1);
      //cerr <<  buffer <<  endl;
      if(pos2 == -1)
	//cerr << "nothing found" << endl;
	continue;
      stringstream field1(buffer.substr(0, pos0));
      stringstream field2(buffer.substr(pos0+2, pos1));
      stringstream field3(buffer.substr(pos1+1, pos2));
      stringstream field4(buffer.substr(pos2+1));
      //field4 >> buffer;

      field1 >> dec >> mb;
      field2 >> dec >> addr;
      field3 >> dec >> reuse;
      field4 >> dec >> offset;
      //cerr << mb << ", " << addr << "," << reuse << "," << offset << endl;
      if(HALO == 0){
	mb = addr >> NUM_MB_BITS;
      }
      mb_counts[mb]++;
      count++;

	//cout << mb << endl;
    }
  }
  

  //Make vector to sort for later
  vector<pair<uint64_t,int> > mb_vec;
  map<uint64_t,int> :: iterator it1;
  for ( it1=mb_counts.begin(); it1 != mb_counts.end(); it1++)
    {
      mb_vec.push_back(make_pair(it1->first, it1->second));
    }

  sort(mb_vec.begin(), mb_vec.end(), sortByVal);
  mb_vec.resize(NUM_REG);
  sort(mb_vec.begin(), mb_vec.end());

  //print the number of memory accesses
  cout << "The number of total accesses is: " << count << endl;

  // print the vector
  cout << "Dominant region counts: [";
  //collect set of MB with most accesses
  vector<uint64_t> dom_mb;
  int dom_count = 0;
  for (int i = 0; i < NUM_REG; i++)
    {
      cout << mb_vec[i].first << ": " << mb_vec[i].second;
      dom_mb.push_back(mb_vec[i].first);
      cout << ", ";
      dom_count += mb_vec[i].second;
    }
  int overflow_count = count - dom_count;
  cout << "-1:" << overflow_count << "]" << endl ;


  sort(dom_mb.begin(),dom_mb.end());
  return dom_mb;


  //return 0;
}

vector<vector<int> > get_reg_traces(vector<uint64_t> dom_mb, char file[]){
  uint64_t mb;
  uint64_t addr;
  int64_t reuse;
  int64_t offset;
  int log_offset;
  size_t pos0;
  size_t pos1;
  size_t pos2;
  uint64_t last_addr[NUM_REG] = {0};

  ifstream tfile;
  vector< vector<int> >  reg_traces;
  for(int i = 0; i < NUM_REG; i++){
    vector<int> vect[NUM_REG];
    reg_traces.push_back(vect[i]);
  }
  vector<int> overflow;
  reg_traces.push_back(overflow);

  tfile.open (file);
  while(!tfile.eof()){
    string buffer;
    getline(tfile, buffer); 
    if(!tfile.eof()) {
      //// EXTRACTING INFORMATION ////
      //4202512,140623034683072, 2, 1
      //std::cout << buffer << endl;

      pos0  = buffer.find(",");
      pos1  = buffer.find(",", pos0+1);
      pos2  = buffer.find(",", pos1+1);

      stringstream field1(buffer.substr(0, pos0));
      stringstream field2(buffer.substr(pos0+2, pos1));
      stringstream field3(buffer.substr(pos1+1, pos2));
      stringstream field4(buffer.substr(pos2+1));

      field1 >> dec >> mb;
      field2 >> dec >> addr;
      field3 >> dec >> reuse;
      field4 >> dec >> offset;
      if(HALO == 0){
	mb = addr >> NUM_MB_BITS;
      }

      

      vector<uint64_t>::iterator it = find(dom_mb.begin(),dom_mb.end(),mb);
      //Selecting region
      int index;
      if(it != dom_mb.end()){
	index = it - dom_mb.begin();
	//cout << index << ", " << mb << ", " << addr << "," << reuse << "," << offset << endl;
      }
      else{
	//Overflow region
	index = NUM_REG;
      }

      //Calculating offset for specified region
      if(HALO == 0){
	
	if(last_addr[index] != 0)
	  offset = addr - last_addr[index];
	else  //Offset is 0 for initial access to the memory region
	  offset = 0;
	last_addr[index] = addr;
      }

      //Selecting offset
      if(offset > 7){
	log_offset = log2(offset/8);
      }
      else if(offset < -7){
	log_offset = log2(-offset/8);
	log_offset = -1 * log_offset;
      }
      else 
	log_offset = 0;
      reg_traces[index].push_back(offset);
      //reg_traces[index].push_back(log_offset);
      //cout << offset << ", " << log_offset << endl;
    }
  }
  for(int i=0; i <= NUM_REG; i++){
    cout << i << ":";
    int length = reg_traces[i].size();
    int toggle = 0;
    for(int x = 0; x < length; x++){
      
      //handling 0
      /*
      if (reg_traces[i][x] == 0){
	if(toggle){
	  toggle = 0;
	  cout << "+";
	}
	else{
	  toggle = 1;
	  cout << "-";
	}
	}*/
      cout << reg_traces[i][x];
      if (x < length -1)
	cout << " ";
      else 
	cout << endl;
    }
  }


}

int print_reg_traces(vector< vector<int> > &reg_log_traces){
  for(int i=0; i <= NUM_REG; i++){
    cout << i << ": ";
    for(int x = 0; x < reg_log_traces[i].size(); x++){
      cout << reg_log_traces[i][x];
      //if x < reg_log_traces[i].size(){
      //  cout << ", ";
      //      }
      //      else:
      //cout << endl;
    }
  }
}





int main(int argc, char*  argv[]) {
    /////////////////////////
    //     parameters      //
    /////////////////////////
    uint64_t pc;
    uint64_t addr;
    int64_t offset;
    uint64_t region;
    uint16_t log_offset;
    bool toggle;
    

    HALO = 1;
    if(argc > 3 ){
      cerr << "Processing file as non-HALO output" << endl;
      HALO = 0;
    }


    //for multi region
    vector<uint64_t> dom_mb = get_region_counts(argv[1]);

    //for multi region
    vector< vector<int> >  reg_log_traces = get_reg_traces(dom_mb, argv[1]);

    //for multiregion
    //print_reg_traces(reg_log_traces);

    return 0;
}
