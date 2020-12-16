#!/usr/bin/env python



def main(in_fname, out_fname):
    with open(in_fname, "r") as in_file:
        for line in in_file:
            data = line.split(",")
            access = "W"
            if(len(data) == 4):

                if(data[3].strip() == "1"):
                    access = "R"
                address = hex(int(data[1].strip())).split('x')[-1]
                print("{} {}".format(address,access))


if __name__ == "__main__":
	from sys import argv
	main(argv[1], argv[2])
