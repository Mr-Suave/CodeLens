#include<bits/stdc++.h>

using namespace std;

void merge(int a[],int begin,int mid,int end){
	int subarr1=mid-begin+1;
	int subarr2=end-mid;
	int sub1[subarr1];
	int sub2[subarr2];
	for(int i=0;i<subarr1;i++){
		sub1[i]=a[begin+i];
	}
	for(int i=0;i<subarr2;i++){
		sub2[i]=a[mid+1+i];
	}
	int j=0;
	int k=0;
	int main=begin;
	while(j<subarr1 && k<subarr2){
		if(sub1[j]<sub2[k]){
			a[main]=sub1[j];
			j++;
		}
		else {
			a[main]=sub2[k];
			k++;
		}
		main++;
	}
	while(j<subarr1){
		a[main]=sub1[j];
		j++;
		main++;
	}
	while(k<subarr2){
		a[main]=sub2[k];
		k++;
		main++;
	}	
}

void mergeSort(int a[] , int begin,int end){
	if(begin>=end)
		return;
	int mid=begin + (end-begin)/2;
	mergeSort(a,begin,mid);
	mergeSort(a,mid+1,end);
	merge(a,begin,mid,end);
}
int main(){

	int a[]={54,26,93,17,77,31,44,55,20,85};
	int length=sizeof(a)/sizeof(a[0]);
	mergeSort(a,0,length-1);
	for(int i=0;i<length;i++){
		cout<<a[i]<<" ";
	}
	cout<<endl;
	cout<<"Enter the element to search"<<endl;
	int x;
	cin>>x;
	int left=0;
	int right=length-1;
	while(left<=right){
		int middle=left +(right-left)/2;
		if(a[middle]==x){
			cout<<"Element is present at index "<<middle<<endl;
			return 0;}
		else if(a[middle]<x)
			left=middle+1;
		else
			right=middle-1;
	}
	cout<<"-1"<<endl;
	return 0;
}