from Tkinter import *
from tkFileDialog import askopenfilename,asksaveasfilename
from tkMessageBox import *


def open_file (): 
	infile = askopenfilename()
	global r1, r2
	r1,r2 = read_Mike11(infile)
	save_file()
	
def save_file():
	
	wel = Tk()
	text = '''
	
Chose the directory and save as .g01 file
	
Click Continue back in the Main Board!
	'''
	
	f = Frame()
	b = Button(f, text = 'Continue', command = open_savefile_directory)
	l = Label(wel,text = text)
	b.pack()
	l.pack()
	f.pack()
	
	mainloop()
	
	
def open_savefile_directory():
	outfile = asksaveasfilename(defaultextension = '.g01',filetypes = [('hec-ras file','*.g01')])
	global r1,r2
	write_hecras(outfile, r1,r2)
	if askyesno('Are you ready to quit?','Done, buddy, go home now!'):
		exit()
	else:
		showinfo("No",'Why you chose to stay....go home!')
	
	
def quit ():
	exit()	

def welcome1():
	
	welcome = '''
WELCOME to this conversion tool.'
version 1.0\nDesigned by Yuanchao XU'\n\n
Working Condition:\n
1. You have to have a mike_11 file, come on!\n
   And that should be in txt type, by default\n
2. You have only one reach in Hec-Ras.\n
3. If you have other requests, plz contact the author by yelling.

NOW OPEN YOUR MIKE_11 FILE!!!!!!!
'''
	wel = Tk()

	f = Frame(wel)
	
	b1 = Button(f,text='Open,The,File',command = open_file)
	b2 = Button(f,text = 'Quit', command = quit)

	b1.pack()
	b2.pack()
	
	l = Label(wel,text = welcome)
	l.pack()
	f.pack()
	
	mainloop()


def read_Mike11 (infile):
	with open(infile) as file:

		chainage_of_all = {}
		#chainage of the river
		chain_in_one_branch = []
		#chainage in each branch
		branch_of_all = {}
		#branches of the river
		branch_name = {}
		#used to store branch names
		crosssections_in_one_branch = []
		#crosssections
		last_branch = 0
		#last branch
		sum_of_branch = 0
		
		'''
		attention, branch_of_all and chain_of_all, they are both dict, so starts 
		with 1, but others are lists, starts from 0
		'''
		
		for line in file:
			
			if line.startswith('Branch'):
				
				line = line.strip()
				branch_name = line.split()[0]
				#this is the branch name
				n_branch = int(branch_name[6:])
				#this the NO of branch, like branch1 and branch2
		
				
				#this part is to get the profiles of crosssections
				
				if n_branch != last_branch:
					sum_of_branch += 1
					
					if sum_of_branch >= 2 :
						
						
						branch_of_all[last_branch] = crosssections_in_one_branch
						#assign cros to dict branch[]
						
						del crosssections_in_one_branch
						'''
						cros can only be deleted, not emptied,
						if delete cros, then create a new one, it's ok.
						if just empty cros, the branch[last_branch] will 
						also be emptied, there were connected through append()
						
						if use empty, better set up a new list, copied from cros,
						copy, not assign, which means
						new_list = cros{:}, not new_list = cros
						'''
						crosssections_in_one_branch = []
						
						chainage_of_all[last_branch] = chain_in_one_branch
						del chain_in_one_branch
						chain_in_one_branch = []
				
					last_branch = n_branch
				
				
				
				#this part is to get the chainage
				chainage = file.next().split()[0] 
				chain_in_one_branch.append(chainage)
			
			
			
			if line.startswith('PROFILE'):
				r_cordi = 0
				#rank of cordinates

				n_cordi = int(line.split()[1])
				#number of cordinates
				
				
				prof = [[ None for i in range(2)] for j in range(n_cordi)]
				#crosssections
				
				for line in file:
					
					if not line.startswith(' '):
						break

						
					
					prof[r_cordi] = [line.split()[0],line.split()[1]]
					
					
					r_cordi += 1
				
				
				crosssections_in_one_branch.append(prof)
				#append new list to the pro list
				
				del prof
				#after appending the list, prof can be emptied
			
			
			
		#if no next branch exsits in the file, the last branch has to be
		#assigned to the dictionary.
				
		branch_of_all[n_branch] = crosssections_in_one_branch
		del crosssections_in_one_branch
				
		chainage_of_all[n_branch] = chain_in_one_branch
		del chain_in_one_branch
			
			
			
	return  branch_of_all, chainage_of_all
	# now every data has been saved in pro list


def write_hecras(outfile,branch_of_all,chainage_of_all):
	'''
	this is only for simple conversion, for example in this case
	we only need one reach, so no need to input number of reaches.
	'''
	chainage_in_hecras = []
	chainage_sum = 0
	#in hecras, we assume all the chainages are in the same reach
	
	
	for i in chainage_of_all:
		chainage_sum += float(chainage_of_all[i][-1])
		#print chainage_of_all[i][-1]
		
	
	for i in chainage_of_all:
		
		for chainage in chainage_of_all[i]:
			
			if float(chainage) == 0 and i != 1:
				continue
			
			new_chainage = chainage_sum - float(chainage)
			if new_chainage <= 0:
				new_chainage = 0
			chainage_in_hecras.append(new_chainage)	
			
		chainage_sum = new_chainage
	print chainage_in_hecras		
	
	'''
	because in Mike11, every branch starts with 0, and this is the same 
	with the last crosssection of last branch
	'''
	
	with open(outfile, 'w') as file:
		
		former_text = '''Geom Title=test
Program Version=4.10
Viewing Rectangle= 0 , 1 , 1 , 0 

River Reach=Yuanchao        ,1               
Reach XY= 2 
 0.45153061224490.834183673469390.441326530612250.30867346938776
0.448979591836740.30612244897959
Rch Text X Y=0.4508929,0.7021684
Reverse River Text= 0'''
		file.write(former_text + '\n' + '\n')
		
		
		r_chainage = 0
		for i in branch_of_all:
			
			for crosssection in branch_of_all[i]:
				
				if crosssection == branch_of_all[i][0] and i != 1:
					continue
				#because in mike, the second branch starts with 0 chainage, so it 
				#is the same with the last chainage of last branch, this should be avoided
				
				
				
				#output1 refers to the information of the reach
				info_of_reach = 'Type RM Length L Ch R = 1 ,'
				other_info = '       ,,,'#here should be the distance of chainages
				output1 = info_of_reach + str(chainage_in_hecras[r_chainage]) + other_info
				file.write(output1 + '\n')
				r_chainage += 1
				
				#time 
				time = 'Node Last Edited Time=Nov/03/2014 14:05:46'
				file.write(time + '\n')
				
				#crosssections
				t_station = '#Sta/Elev= '
				station = str(len(crosssection))
				output2 = t_station + station
				file.write(output2 + '\n')
					
				n = 0	
				for cordi in crosssection:
					
					if n%5 == 0 and n != 0:
						file.write('\n')
						
					file.write('%8s%8s' % (cordi[0],cordi[1]))
					n += 1
				file.write('\n')
				
				#Manning coefficient
				Manning = '#Mann= 0 , 0 , 0'
				file.write(Manning + '\n')
				
				
				#Bank station
				Bank_sta = 'Bank Sta=,'
				file.write(Bank_sta + '\n')
				
				#XS rating curve
				xs_rating = 'XS Rating Curve= 0 ,0'
				file.write(xs_rating + '\n')
				
				#Exp/Cntr
				exp_cntr = 'Exp/Cntr=.3,.1'
				file.write(exp_cntr + '\n' + '\n')
		
		
		#end of chianage
		chan_stop = 'Chan Stop Cuts=-1'
		file.write(chan_stop + '\n')
		
		#newline
		for n_new_lines in range(3):
			file.write('\n')
		
		#end of file
		end_of_file = '''Use User Specified Reach Order=0
GIS Ratio Cuts To Invert=-1
GIS Limit At Bridges=0
Composite Channel Slope=5'''
		file.write(end_of_file + '\n')



#infile = raw_input("Input the route of mike11 file, you're gonna read it.\n\
#for example: E:\\1\\python\\mike11.txt\nInput here:")		
#outfile = raw_input("Input the route of hec-ras file, you;re gonne write it.\nInput here:")
#file = 'E:\\1\\Python\\data_process\\Mike11.txt'
#branch_of_all, chainage_of_all = read_Mike11(infile)
#print branch_of_all[9]
#print chainage_of_all

#outfile = "E:\\1\\Python\\data_process\\outfile.txt"
#outfile = "E:\\1\\HEC-RAS\\test.g01"
#write_hecras(outfile, branch_of_all, chainage_of_all)

welcome1()


