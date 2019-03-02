#include <stdio.h>
#include <stdlib.h>
#include <string.h>



typedef struct edge {

	int u, v, w;

} edge;

typedef struct kume {

	int size;
	int elemanlar[100];

} kume;

void sort(int n, edge edges[]);
int readFile(int matrix[100][100]);
void clusterElementsDisplay(int labelCnt, int size, int label[], kume kumeler[]);
void doClustering(int k, int size, edge edges[], int label[], kume kumeler[]);
void minLengthBul(int kume1[], int sizeKume1, int kume2[], int sizeKume2,int matrix[100][100]);

void sort(int n, edge edges[]) { // selection sort ile graf kenarlarini siralayarak bir struc dizisinde tutar.

	int c;
	int d;
	int position;
	edge swap;

	for (c = 0; c < (n - 1); c++) {
		position = c;

		for (d = c + 1; d < n; d++) {
			if (edges[position].w > edges[d].w)
				position = d;
		}
		if (position != c) {
			swap = edges[c];
			edges[c] = edges[position];
			edges[position] = swap;
		}
	}

}

void clusterElementsDisplay(int labelCnt, int size, int label[], kume kumeler[]) { //kumeleri ekrana basar ve bu kumeleri bir struct dizisinde saklar.

	int i;
	int b;
	int flag;
	int flag2;
	int sizeCnt;
	int kumeAdr;

	for (i = 0; i < size; i++) {

		if (label[i] == 0) {

			printf("%d etiketli kume : ", i);
			printf("%d\n", i);
			kumeler[i].size = 1;
			kumeler[i].elemanlar[0] = i;

		}

	}



	for (i = 1; i <= labelCnt; i++) {
		flag = 0;
		flag2 = 0;
		sizeCnt = 0;
		for (b = 0; b < size; b++) {

			if (label[b] == i) {

				if (!flag2) {

					kumeAdr = b; // label dizisinde buluna i etiketli ilk dugum, ilgili kumenin etiketi olarak set edilir.
					printf("%d etiketli kume : ", kumeAdr);

				}

				flag2 = 1;

				flag = 1;
				printf("%d ", b);
				kumeler[kumeAdr].elemanlar[sizeCnt] = b;
				sizeCnt++;

			}

		}

		if (flag == 1) {

			kumeler[kumeAdr].size = sizeCnt;
			printf("\n");

		}

	}

}

void doClustering(int k, int size, edge edges[], int label[], kume kumeler[]) { //kruskal mst kullanarak kumeleme islemini gerceklestirir.

	int totalClusters = size;
	int u;
	int v;
	int i = 0;
	int labelCnt = 0;
	int b;

	while (totalClusters > k) {

		u = edges[i].u;
		v = edges[i].v;

		if (label[u] + label[v] == 0) {

			labelCnt++;
			label[u] = labelCnt;
			label[v] = labelCnt;
			totalClusters--;

		}

		else {

			if (label[u] != label[v]) {
				totalClusters--;

				if (label[u] == 0) {

					label[u] = label[v];

				}

				else {

					if (label[v] == 0) {

						label[v] = label[u];

					}

					else {

						int lbl = label[u];

						for (b = 0; b < size; b++) {

							if (label[b] == lbl) {

								label[b] = label[v];

							}

						}

					}

				}

			}

		}

		i++;

	}

	clusterElementsDisplay(labelCnt, size, label, kumeler);

}

int readFile(int matrix[100][100]) { //dosyadan okuma yapar ve okunan matrisin size ini doner.

	FILE* fp;
	char *token;
	int converted;
	int count1 = 0;
	int count2 = 0;

	char str[1000];
	const char s[2] = ",";

	fp = fopen("data.txt", "r");

	while (fscanf(fp, "%s", str) >= 1) {

		token = strtok(str, s);

		count2 = 0;
		while (token != NULL) {

			converted = atoi(token);
			matrix[count1][count2] = converted;
			token = strtok(NULL, s);

			count2++;

		}

		count1++;

	}

	return count1;

}

void minLengthBul(int kume1[], int sizeKume1, int kume2[], int sizeKume2,int matrix[100][100]) { //minLength[3] = u w v , kume1 ve kume2 olarak gonderilen kumelerin arasindaki en kisa mesafeyi bulur.

	readFile(matrix);

	int i;
	int k;
	int flag = 0; // mesafesi sifir olmayan ilk iki dugumu bulmak icin
	int minLength[3];
	int initLength;

	for (i = 0; i < sizeKume1; i++) {

		for (k = 0; k < sizeKume2; k++) {

			initLength = matrix[kume1[i]][kume2[k]];

			if (!flag) {

				if ((initLength != 0)) {

					minLength[1] = initLength; //min length ik olarak iki kumenin ilk elemanlarýnýn arasýndaki mesafeye set edilir.
					minLength[0] = kume1[i];
					minLength[2] = kume2[k];
					flag = 1;

				}

			}

			else if ((initLength < minLength[1]) && (initLength != 0)) {

				minLength[1] = initLength;
				minLength[0] = kume1[i];
				minLength[2] = kume2[k];

			}

		}

	}

	printf("En kisa mesafe : %d\n", minLength[1]);
	printf("Dugumler : %d - %d", minLength[0], minLength[2]);

}

int main(int argc, char *argv[]) {

	int i;
	int k;
	int size;
	int edgeCnt = 0;
	int matrix[100][100];
	edge edges[100];
	int label[100];
	kume kumeler[100];
	int etiket1;
	int etiket2;

	size = readFile(matrix);

	for (i = 0; i < size; i++) { // graf kenarlarini ayirma islemi.
		for (k = i + 1; k < size; k++) {

			if ((matrix[i][k] != 0)) {

				edges[edgeCnt].u = i;
				edges[edgeCnt].v = k;
				edges[edgeCnt].w = matrix[i][k];
				edgeCnt++;

			}

		}

	}

	sort(edgeCnt, edges);

	for (i = 0; i < size; i++) {

		label[i] = 0;

	}

	printf("k sayisini giriniz : ");
	scanf("%d", &k);

	doClustering(k, size, edges, label, kumeler);

	printf("\n");
	printf("Hangi etiketli iki kume arasindaki en kisa mesafe bulunsun?\n");
	printf("1. kume etiketi : ");
	scanf("%d", &etiket1);
	printf("2. kume etiketi : ");
	scanf("%d", &etiket2);
	printf("\n");

	minLengthBul(kumeler[etiket1].elemanlar, kumeler[etiket1].size,
			kumeler[etiket2].elemanlar, kumeler[etiket2].size, matrix);



	return 0;
}

