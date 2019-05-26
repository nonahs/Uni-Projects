/* LC-3 Disassembler for ADD, AND, JMP and BR opcodes */

#include <stdio.h>
#include <stdlib.h>

	//Masks
	int opcodeMask = 0xF000; 		//bit 12
	int destRegMask = 0x0E00; 		//bit 9
	int sourceRegMask = 0x01C0;		//bit 6
	int sourceReg2Mask = 0x0007;	//bit 0
	int immediateMask = 0x0020;		//bit 5
	int immValueMask = 0x000F;		//bit 0
	int immSignMask = 0x0010;		//bit 4
	int brnMask = 0x0800;			//bit 11
	int brzMask = 0x0400;			//bit 10
	int brpMask = 0x0200;			//bit 9
	int brSignMask = 0x0100;		//bit 8
	int brAddMask = 0x00FF;			//bit 0
	
	//Variables
	int opcode;
	int destReg;
	int sourceReg1;
	int sourceReg2;
	int immValue;
	int immSign;
	int brn, brz, brp;
	int brAdd, brSign;
	//int pcadd = 0x3000;
	int pcadd;

int main(int argc, char const *argv[]) {
	
	if (argc != 3) {
		printf("Please specify a file to read from and starting address\n");
		return 1;
	}
	
	FILE *file;
	int hex;
	
	//file = fopen("obj", "r");
	file = fopen(argv[1], "r");
	if (file == NULL) {
		printf("File Not Found\n");
		return 1;
	}
	
	pcadd = strtol(argv[2], NULL, 16);
	//printf("0x%04x starting address\n", pcadd);
	
	while (fscanf(file, "%x", &hex) != EOF) {
		//printf("0x%04x ",pcadd);
		pcadd++; //increment the pc
		opcode = (hex & opcodeMask) >> 12;
		
		switch (opcode) {
			case 0x1: //ADD
			destReg = (hex & destRegMask) >> 9;
			sourceReg1 = (hex & sourceRegMask) >> 6;
			if ((hex & immediateMask) >> 5) { //Immediate mode
				immValue = (hex & immValueMask);
				if (immSign = (hex & immSignMask) >> 4) //Sign is Negative
					immValue = immValue - 16;
				printf("add r%x,r%x,%d\n", destReg, sourceReg1, immValue); // Immediate
			}
			else {
				sourceReg2 = (hex & sourceReg2Mask);
				printf("add r%x,r%x,r%x\n", destReg, sourceReg1, sourceReg2);
			}
			break;
			
			case 0x5: //AND
			destReg = (hex & destRegMask) >> 9;
			sourceReg1 = (hex & sourceRegMask) >> 6;
			if ((hex & immediateMask) >> 5) { //Immediate mode
				immValue = (hex & immValueMask);
				if (immSign = (hex & immSignMask) >> 4) //Sign is Negative
					immValue = immValue - 16;
				printf("and r%x,r%x,%d\n", destReg, sourceReg1, immValue); // Immediate
			}
			else {
				sourceReg2 = (hex & sourceReg2Mask);
				printf("and r%x,r%x,r%x\n", destReg, sourceReg1, sourceReg2);
			}
			break;
			
			case 0xc: //JMP
			sourceReg1 = (hex & sourceRegMask) >> 6; //BaseR
			printf("jmp r%x\n", sourceReg1);
			break;
			
			case 0x0: //BR
			printf("br");
			if ((hex & brnMask) >> 11)
				printf("n");
			if ((hex & brzMask) >> 10)
				printf("z");
			if ((hex & brpMask) >> 9)
				printf("p");
			brAdd = (hex & brAddMask) + pcadd;
			if (brSign = (hex & brSignMask) >> 8) //Sign is Negative
				brAdd = ((hex & brAddMask) + pcadd) - 256;
			printf(" 0x%04x\n",brAdd);
			break;
			
		}
	}
	
	fclose(file);
	
	return 0;
}