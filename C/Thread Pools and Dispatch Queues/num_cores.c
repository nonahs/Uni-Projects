#include <stdio.h>
#include <sys/sysinfo.h>
#include <unistd.h>

int main(int argc, char** argv) {

	//int processors = get_nprocs_conf(); //configured
	//int processors_a = get_nprocs(); //available
	int processors = sysconf(_SC_NPROCESSORS_ONLN);
	
	//printf("Number of cores configures %d and %d cores available\n", processors_a, processors);
	printf("This machine has %d cores.\n", processors);
	
	return 0;
}