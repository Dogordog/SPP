extern "C"{
	#include "evalHandTables.h"
}
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include<unordered_map> 

using namespace std;  


void evalShowdown(int board[], int hole[][2], int player_number, int hs[]){
	Cardset public_cs = emptyCardset();
	for(int i=0; i<5; i++){
		addCardToCardset(&public_cs, board[i]%4, board[i]/4);
	}
	
	for(int i=0; i<player_number; i++) {
		Cardset cs = public_cs;
		addCardToCardset(&cs, hole[i][0]%4, hole[i][0]/4);
		addCardToCardset(&cs, hole[i][1]%4, hole[i][1]/4);
		hs[i] = rankCardset(cs);
	}

	// for (int i=0; i<player_number; i++){
	// 	printf("%d\n", hs[i]);
	// }
}

int sample_win_pr(int board[], int hole[], int opponent_number, int board_count){
	if (board_count == 5) {

	}
}

double sample_5board_win_pr(int board[], int hole[], int opponent_number, int iteration){
	// sample [non-conflict] opponent hole
	Cardset public_cs = emptyCardset();
	for(int i=0; i<5; i++){
		addCardToCardset(&public_cs, board[i]%4, board[i]/4);
	}

	// compute hole cards strength
	Cardset hole_cs = public_cs;
	addCardToCardset(&hole_cs, hole[0]%4, hole[0]/4);
	addCardToCardset(&hole_cs, hole[1]%4, hole[1]/4);
	int hole_hs = rankCardset(hole_cs);

	// generate all possible 
	// [1.record used cards 2.pre-compute hand strength lookup table 3.generate non-conflict opponent holes]
	// [1]
	unordered_map<int, int> used_cards;
	for (int i=0; i<52; i++){
		used_cards[i] = 0;
	} // init
	for (int i=0; i<5; i++){
		used_cards[board[i]] = 1;
	}
	used_cards[hole[0]] = 1;
	used_cards[hole[1]] = 1;

	// [2]
	int table[52][52];
	for(int i=0; i<51; i++){
		for(int j=i+1; j<52; j++){
			if(used_cards[i] == 0 && used_cards[j] == 0){
				Cardset opponent_cs = public_cs;
				addCardToCardset(&opponent_cs, i%4, i/4);
				addCardToCardset(&opponent_cs, j%4, j/4);
				table[i][j] = rankCardset(opponent_cs);
				table[j][i] = table[i][j];
			} else {
				table[i][j] = -1;
				table[j][i] = -1;
			}
		}
	}
	// [3] generate opponent_number opponent holes from 52 - 2 - 5 = 45 cards
	int valid_cards[45];
	int idx = 0;
	for(int i=0; i<52; i++){
		if(used_cards[i] == 0){
			valid_cards[idx] = i;
			idx++;
		}
	} // construct array containing 45 valid cards

	double win_count = 0;
	for(int t=0; t<iteration; t++){

		int flag = 1; // 0 for tie, 1 for win, -1 for lose

		// select (2 * opponent_number) cards from 45 cards
		int opponent_holes[2 * opponent_number];
		for(int i=0; i< 2*opponent_number; i++){
			int index = rand() % (45-i);
			opponent_holes[i] = valid_cards[index];
			int temp = valid_cards[45-i-1];
			valid_cards[45-i-1] = index;
			valid_cards[index] = temp;
		}

		int tie_number = 0;
		for(int i=0; i < opponent_number; i++){
			int card1 = opponent_holes[2*i];
			int card2 = opponent_holes[2*i + 1];
			int opponent_hs = table[card1][card2];
			if(opponent_hs > hole_hs) {
				flag = -1;
				break;
			} else if(opponent_hs == hole_hs){
				flag = 0;
				tie_number++;
			}
		}

		if(flag == 1){
			win_count++;
		} else if(flag == 0) {
			win_count += 1.0 / tie_number;
		}
	}
	
	return win_count / iteration;
}

int main(int argc, char const *argv[])
{
	int board[] = {0,12,19,11,33};
	int one_hole[] = {9,34};
	// evalShowdown(board, hole, 3, hs);
	double res = sample_5board_win_pr(board,one_hole,1,1000000);
	cout<<res<<endl;
	return 0;
}

int add(int a, int b){
	return a + b;
}





// generate lib.so
// gcc eval.cpp -fPIC -shared -o lib.so

// python3 test.py to call add function of lib.so

