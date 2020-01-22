# -*- coding:  ISO-8859-1 -*-
#	         /**************************************
#	        *     AUTHOR: Federico Tomassini        *
#	       *     Copyright (C) Federico Tomassini    *
#	      *     Contact effetom@gmail.com             *
#	     ***********************************************
#	     *******                                ********
#*************************************************************************
#*                                             				 *
#*  This program is free software; you can redistribute it and/or modify *
#*  it under the terms of the GNU General Public License as published by *
#*  the Free Software Foundation; either version 2 of the License, or	 *
#*  (at your option) any later version.					 *
#*									 *
#*  This program is distributed in the hope that it will be useful,	 *
#*  but WITHOUT ANY WARRANTY; without even the implied warranty of	 *
#*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the	 *
#*  GNU General Public License for more details.			 *
#*									 *
#************************************************************************/
def find_min_in_row(A,i):
	""" Trova il minimo su una riga 
	di una matrice la matrice è espressa come lista di liste-righe """
	min=A[i][0]
	for item in A[i][1:]:
		if item<min:
			min=item
	return min
def find_min_in_col(A,i):
	""" Trova il minimo su una colonna 
	di una matrice la matrice è espressa come lista di liste-righe """
	min=A[0][i]
	j=1
	while j<len(A):
		if A[j][i]<min:
			min=A[j][i]
		j+=1
	return min

def substract_const_row(A,i,c):
	""" Sottrae c ad ogni elemento della riga i della matrice A """
	j=0
	while j<len(A[i]):
		A[i][j]=A[i][j]-c
		j=j+1

def substract_const_col(A,i,c):
	""" Sottrae c ad ogni elemento della colonna i della matrice A """
	j=0
	while j<len(A):
		A[j][i]=A[j][i]-c
		j=j+1

def there_s_star_in_row(A,i,j,starred):
	""" i è la riga, j l'elemento di riga da non considerare, starred la lista degli star """
	lista_temp=range(len(A[i]))
	lista_temp.remove(j)
	for item in lista_temp:
		if (i,item) in starred:
			return item
	return -1

def there_s_star_in_column(A,i,j,starred):
	""" i è la colonna, j l'elemento di colonna da non considerare, starred la lista degli star """
	lista_temp=range(len(A))
	lista_temp.remove(j)
	for item in lista_temp:
		if (item,i) in starred:
			return item
	return -1

def hungarian_method(A):
	""" Resolve problem of matching and return the list of pairs 'result' """
	ind_row=range(len(A))
	ind_col=range(len(A[0]))
	starred=[]
	primed=[]
	cover_col=[]
	cover_row=[]
	# preparazione iniziale della matrice
	# le righe vengono scalate di modo che il min su ogni riga è zero
	# MICHI: CAMBIATO RUGHE COLONNE
	for j in ind_col:
		substract_const_col(A,j,find_min_in_col(A,j))
	# aggiungere star a starred inizialmente e con poche condizioni:
	# l'algoritmo vero e proprio deve ancora cominciare
	for i in ind_row:
		[starred.append((i,j)) for j in ind_col if A[i][j]==0 and there_s_star_in_column(A,j,i,starred)==-1 and there_s_star_in_row(A,i,j,starred)==-1]
	for i in starred:
		cover_col.append(i[1])
	# ora comincia l'algoritmo serio
	while len(cover_col)!=len(ind_col):
		find_and_prime(A,cover_col,cover_row,starred, primed,ind_col,ind_row)
		for i in starred:
			cover_col.append(i[1])
	return starred
	

def find_and_prime(A,cover_col,cover_row,starred, primed,ind_col,ind_row):
	""" Il cuore del programma che decide come avanzare nel calcolo """
	uncov=find_uncovered_zeros(A,cover_row,cover_col,ind_row,ind_col)
	if uncov==0:
		rescale_uncover_matrix(A,cover_row,cover_col,ind_row,ind_col)
		uncov=find_uncovered_zeros(A,cover_row,cover_col,ind_row,ind_col)
	while 1:
		primed.append(uncov)
		temp=there_s_star_in_row(A,uncov[0],uncov[1],starred)
		if temp!=-1:
			cover_row.append(uncov[0])
			cover_col.remove(temp)
			uncov=find_uncovered_zeros(A,cover_row,cover_col,ind_row,ind_col)
			if uncov==0:
				rescale_uncover_matrix(A,cover_row,cover_col,ind_row,ind_col)
				uncov=find_uncovered_zeros(A,cover_row,cover_col,ind_row,ind_col)
		else:
			zed_series(A,cover_row,cover_col,ind_row,ind_col,starred,primed)
			break
def zed_series(A,cover_row,cover_col,ind_row,ind_col,starred,primed):
	star_serie=[]
	prime_serie=[]
	(i,j)=primed[-1]
	prime_serie.append( (i,j) )
	i=there_s_star_in_column(A,j,i,starred)
	while i!=-1:
		star_serie.append( (i,j) )
		j=there_s_star_in_row(A,i,j,primed)
		prime_serie.append( (i,j) )
		i=there_s_star_in_column(A, j,i,starred)
	for i in star_serie:
		starred.remove(i)
	for i in prime_serie:
		starred.append(i)
	del primed[:]
	del cover_row[:]
	del cover_col[:]
		
	
def rescale_uncover_matrix(A,cover_row,cover_col,ind_row,ind_col):
	min=find_uncovered_min(A,cover_row,cover_col,ind_row,ind_col)
	new_ind_row=ind_row[:]
	new_ind_col=ind_col[:]
	for i in cover_row: new_ind_row.remove(i)
	for i in cover_col: new_ind_col.remove(i)
	for i in new_ind_row:
		for j in new_ind_col:
			A[i][j]=A[i][j]-min 
def find_uncovered_zeros(A,cover_row,cover_col,ind_row,ind_col):
	new_ind_row=ind_row[:]
	new_ind_col=ind_col[:]
	for i in cover_row: new_ind_row.remove(i)
	for i in cover_col: new_ind_col.remove(i)
	for i in new_ind_row:
		for j in new_ind_col:
			if A[i][j]==0: 
				return (i,j)
	return 0
def find_uncovered_min(A,cover_row,cover_col,ind_row,ind_col):
	new_ind_row=ind_row[:]
	new_ind_col=ind_col[:]
	for i in cover_row: new_ind_row.remove(i)
	for i in cover_col: new_ind_col.remove(i)
	min=A[new_ind_row[0]][new_ind_col[0]]
	for i in new_ind_row:
		for j in new_ind_col:
			if A[i][j]<min: min=A[i][j]  
	return min
def take_from_file(nome):
	fil=open(nome,'r')
	A=[]
	ss=fil.readline()
	ss=fil.readline()
	listaa=[]
	while (ss):
		tt=ss.split(' ')
		tt=tt[:len(tt)-1]
		for i in tt:
			listaa.append(float(i))
		A.append(listaa)
		ss=fil.readline()
	return A
	
	

	
if __name__== "__main__":
	from random import *
# Define a matrix
	#A=[ [1,2,3],[2,4,6],[3,6,9]]
# Random matrix
	#lin=[]
	#for i in range(10):
	#	for j in range(10):
	#		lin.append(randrange(1,100))
	#	A.append(lin[:])
	#	del lin[:]
# Matrix from file
	#A=take_from_file('prova')
	A=[ [-1,-2,-3],[-2,-4,-6],[-3,-6,-9]]
	A=[ [0,0],[-9,-10],[0, -9] ]
	solve=hungarian_method(A)
	print(solve)
