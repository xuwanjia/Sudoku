#include<time.h>
#include<stdlib.h>
#include<stdio.h>

#define N (3)
#define M (N*N)
#define MAXCOL (M*M*4)
#define MAXNODE (M*M*M*4+MAXCOL+1)

#define F(i,A,s) for(int i=A[s];i!=s;i=A[i])

void DLXsolve(int* sdk){

	struct timespec time_start={0,0},time_end={0,0};

	clock_gettime(CLOCK_REALTIME,&time_start);

	int sz=0;
	int ansd=0;
	int solved=0;
	int tot=0;

	int ans[M*M];
	int buf[M*M]={};

	int O[M][M][M]={};

	int row[MAXNODE];
	int col[MAXNODE];

	int L[MAXNODE];
	int R[MAXNODE];
	int U[MAXNODE];
	int D[MAXNODE];

	int Count[MAXCOL+1]={};
	int Prev[MAXCOL+1+M+1];
	int Next[MAXCOL+1+M+1];

	inline void del(int x){
		Next[Prev[x]]=Next[x];
		Prev[Next[x]]=Prev[x];
	}

	inline void res(int x){
		int y=Count[x]+1+MAXCOL;
		Prev[x]=y;
		Next[x]=Next[y];
		Next[Prev[x]]=x;
		Prev[Next[x]]=x;
	}

	inline void inc(int x){
		del(x);
		Count[x]++;
		res(x);
	}

	inline void dec(int x){
		del(x);
		Count[x]--;
		res(x);
	}

	inline int getmin(){
		int i=MAXCOL+1;
		while(Next[i]==i) ++i;
		return Next[i];
	}

	void init(int n){
		for(int i=0;i<=n;++i){
			U[i]=i;
			D[i]=i;
			L[i]=i-1;
			R[i]=i+1;
		}
		R[n]=0;
		L[0]=n;
		sz=n+1;
		for(int i=0;i<=M;++i)
		    Next[i+MAXCOL+1]=i+MAXCOL+1;
		for(int i=0;i<=M;++i)
		    Prev[i+MAXCOL+1]=i+MAXCOL+1;
		for(int i=1;i<=MAXCOL;++i) res(i);
	}

	void add(int r,int* a,int n){
		int first=sz;
		for(int i=0;i<n;++i){
			int c=a[i];
			L[sz]=sz-1;
			R[sz]=sz+1;
			D[sz]=c;
			U[sz]=U[c];
			D[U[c]]=sz;
			U[c]=sz;
			row[sz]=r;
			col[sz]=c;
			sz++;
			inc(c);
		}
		R[sz-1]=first;
		L[first]=sz-1;
	}

	void rm(int c){
		del(c);
		L[R[c]]=L[c];
		R[L[c]]=R[c];
		F(i,D,c) 
			F(j,R,i){
				U[D[j]]=U[j];
				D[U[j]]=D[j];
				dec(col[j]);
			}
	}

	void rt(int c){
		res(c);
		F(i,U,c) 
			F(j,L,i){
				U[D[j]]=j;
				D[U[j]]=j;
				inc(col[j]);
			}
		L[R[c]]=c;
		R[L[c]]=c;
	}

	int dfs(int d){
		++tot;
		if(!R[0]){
			if(solved){
				solved=2;
				return 1; 
			}
			else{
				solved=1;
				ansd=d;
				for(int i=0;i<ansd;++i) buf[i]=ans[i];
				return 0;
			}
		}
		int c=getmin();
		rm(c);
		F(i,D,c){
			ans[d]=row[i];
			F(j,R,i) rm(col[j]);
			if(dfs(d+1)) return 1;
			F(j,L,i) rt(col[j]);
		}
		rt(c);
		return 0;
	}

	int en(int a,int b,int c){
		return a*M*M+b*M+c+1;
	}

	init(MAXCOL);

	for(int r=0;r<M;++r)
		for(int c=0;c<M;++c)
			if(sdk[r*M+c]){
				int v=sdk[r*M+c]-1;
				for(int i=0;i<M;++i) O[r][i][v]=1;
				for(int i=0;i<M;++i) O[i][c][v]=1;
				O[r][c][v]=0;
			}

	for(int r=0;r<M;++r)
		for(int c=0;c<M;++c)
			for(int v=0;v<M;++v)
				if(!O[r][c][v] && (!sdk[r*M+c] || sdk[r*M+c]==v+1)){
					int a[4]={
						en(0,r,c),
						en(1,r,v),
						en(2,c,v),
						en(3,(r/N)*N+c/N,v)
					};
					add(en(r,c,v),a,4);
				}

	dfs(0);

	for(int i=0;i<ansd;++i){
		int k=buf[i]-1;
		int a,b,c;
		c=k%M;k/=M;
		b=k%M;k/=M;
		a=k;
		sdk[a*M+b]=c+1;
	}

	clock_gettime(CLOCK_REALTIME,&time_end);

	sdk[81]=solved;
	sdk[82]=tot;

	sdk[83]=time_end.tv_sec-time_start.tv_sec;
	sdk[84]=time_end.tv_nsec-time_start.tv_nsec;

}


void DLXgenerate(int* f,int* sdk){
    int dfs(int* sdk){
        int a[100];
        for(int i=0;i<M*M;++i) a[i]=sdk[i];
        DLXsolve(a);
        if(a[81]==2) return 0;
        for(int i=0;i<M*M;++i)
            if(sdk[f[i]]){
                int x=sdk[f[i]];
                sdk[f[i]]=0;
                if(dfs(sdk)) return 1;
                sdk[f[i]]=x;
            }
        return 1;
    }
    srand(f[M*M]);
    while(1){
        for(int i=0;i<M*M;++i) sdk[i]=0;
        for(int i=1;i<=M;++i) sdk[rand()%81]=i;
        DLXsolve(sdk);
        if(sdk[81]) break;
    }
    dfs(sdk);
}