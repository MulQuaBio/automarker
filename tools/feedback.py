"""
	Automated testing, logging (including feedback) on MQB computing practical
	work.  

	USAGE: 
	
	`python3 feedback.py StudentsFile RepoPath FileList`

	or, if ready to git push: 
	
	`python3 feedback.py StudentsFile RepoPath FileList --git_push`

	example: `python3 feedback.py
	~/Documents/Teaching/IC_CMEE/2020-21/Students/Students.csv
	~/Documents/Teaching/IC_CMEE/2020-21/Coursework/StudentRepos FileList`

	ARGUMENTS: 

	StudentsFile  : FULL path to input file containing student data, 
	                including git repo address

	RepoPath      : FULL path to location for students' local git       
	                repositories (without an ending "/")

	FileList      : FULL path to text file containing list of files to check for
	                and test. If file is empty (allowed), all code/script files will be tested, and no feedback given on missing files.    

    --git_pull     : Optional flag indicating whether to pull students' 
	                git repositories only, without testing (default is False).
	                Only works if the student's repo already exists

	--git_push     : Optional flag indicating whether to push the testing
                    results to students' git repositories (default is False). If
                    used contents of feedback directory are pushed, nothing else
"""

	# You are an expert computer programmer.

	# Based on the attached log files, provide detailed, constructive, feedback on the project structure & workflow (including the README file(s)), and code structure, syntax, and errors generated in each week.

	# Include *every* code and script file tested in the weekly log files.

	# Comment on improvements made by comparing each week's previous and new log file. 

	# Comment on quality of formatting of the outputs of files. 

	# Use past tense and personal speech.

	# Provide separate feedback on code and latex report corresponding to the florida autocorrelation temperatures practical. 

	# Structure feedback by week with a summary at the end .

	# Provide feedback on git practices using the attached git log output, focusing on how much the student improved specific scripts across the weeks. Also comment on size of the git repo if its too large (binary files committed).

	# Do not include an "Overview" section describing the document. 

	# Include Student's name at the top of the file.

	# Return the feedback as a markdown (*.md) file for download, naming it "Final_Assessment_" followed by student's first name.

##################################

# You are an expert computer programmer

# Based on the attached log file, provide detailed, constructive, feedback on the group project structure & workflow (including the README file(s)), and code structure, syntax, and errors generated.

# Include every code and script file.

# Provide separate, specific feedback on the florida autocorrlation practical code and writeup with reference to practical brief: https://mulquabio.github.io/MQB/notebooks/R.html#groupwork-practical-autocorrelation-in-florida-weather.

# Use past tense

# Also provide feedback on git practices using the git log output included in the log file. Identify degree of contributions of the different team members.

# Return the feedback as a markdown (*.md) file for download, prefixing group name and "Final_Assessment_and_" to original log file name.

################ Imports #####################

import subprocess, os, csv, argparse, re, time

################ Functions #####################
def run_popen(command, timeout):
	""" 
	Runs a sub-program in subprocess.Popen using the given COMMAND and
	TIMEOUT (seconds). Requires the `time` module. 
	"""

	start = time.time()

	p = subprocess.Popen('timeout ' + str(timeout) + 's ' + command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	try:
		stdout, stderr = p.communicate(timeout=timeout)
	except subprocess.TimeoutExpired:
		p.kill()
		stdout, stderr = p.communicate()

	end = time.time()

	return p, stdout.decode(), stderr.decode(), (end - start) # decode: binary --> string

##################### Main Code #####################

# set up the argument parser
parser = argparse.ArgumentParser()

# positional argument inputs
parser.add_argument("StudentsFile", help="Input file containing student details (full path)")
parser.add_argument("RepoPath", help="Location for git repositories (full path)")
parser.add_argument("FileList", help="Location of (text) file (full path) containing list of files to test")

# expectedFiles = exp_files(args)  # Import list of expected files, on a per-week basis; not currently used 

# Optional argument inputs
parser.add_argument("--git_pull", action="store_true", 
								 dest="git_pull", default=False,
								 help="Whether to *only* git pull students' repositories (no code testing) ")

parser.add_argument("--git_push", action="store_true", 
								dest="git_push", default=False,
								help="Whether to *only* git push testing results to students' repositories")

args = parser.parse_args() 

with open(args.StudentsFile,'r') as f: # Read in and store the student data
	csvread = csv.reader(f)
	Stdnts = [tuple(row) for row in csvread]

with open(args.FileList,'r') as f: # Read in and store the file list
	csvread = csv.reader(f)
	ExpFiles = [tuple(row) for row in csvread]

Hdrs = Stdnts[0] #store headers
Stdnts.remove(Hdrs) #remove header row 

scrptPath = os.path.dirname(os.path.realpath(__file__)) #store feedback script path
timeout = 10 #set time out for each script's run (integer seconds)
charLim = 500 #set limit to output of each script's run to be printed

for Stdnt in Stdnts:

	Name = (Stdnt[Hdrs.index('first_name')] + Stdnt[Hdrs.index('second_name')]+ '_' + Stdnt[Hdrs.index('username')]).replace(" ","").replace("'","") #Remove any spaces from name
	RepoPath = args.RepoPath + '/' + Name
	AzzPath = RepoPath + '/Feedback'
	
	if args.git_push:
		
		print("...\n\n" + "Git pushing testing results for " + Stdnt[Hdrs.index('first_name')] + " "+ Stdnt[Hdrs.index('second_name')] + "...\n\n")

		subprocess.check_output(["git","-C", RepoPath, "add", os.path.basename(AzzPath) + "/*"])  # Add *only* testing results

		subprocess.check_output(["git","-C", RepoPath, "commit","-m","Pushed testing results"])
				
		subprocess.check_output(["git","-C", RepoPath,"push", "origin", "HEAD"])
		
		subprocess.check_output(["git","-C", RepoPath, "reset","--hard"]) # discard everything else among the tracked content that was changed

		subprocess.check_output(["git","-C", RepoPath, "clean","-fdx"]) # get rid of untracked files (-f) and directories (-d) in local copy. -x to also remove ignored files

		continue

	if args.git_pull:
		print("...\n\n"+"Pulling repository for "+ Stdnt[Hdrs.index('first_name')] + " "+ Stdnt[Hdrs.index('second_name')] + "...\n\n")		
		if os.path.exists(RepoPath): # only if the repo exists already

			subprocess.check_output(["git","-C", RepoPath, "reset","--hard"]) # discard everything in the local tracked content that has been changed
			
			subprocess.check_output(["git", "-C", RepoPath, "pull"])
		
		else: # Otherwise, clone repo first time
			print("...\n\n"+"Student's repository does not exist; Cloning it...\n\n")
		
			subprocess.check_output(["git","clone", Stdnt[Hdrs.index('git_repo')], RepoPath])
		
		continue
	
	if not os.path.exists(RepoPath): # Clone repo first time if it does not already exist
		print("...\n\n"+"Student's repository does not exist; Cloning it...\n\n")
		
		subprocess.check_output(["git","clone", Stdnt[Hdrs.index('git_repo')], RepoPath])

		continue

	else:

		subprocess.check_output(["git","-C", RepoPath,"pull"])

		p, output, err, time_used = run_popen("git -C " + RepoPath + " count-objects -vH", timeout)

		Keys = list([row.split(': ')[0] for row in output.splitlines()])
		Vals = list([row.split(': ')[1] for row in output.splitlines()])
		RepoStats = dict(zip(Keys, Vals))

	#~ Now open feedback directory inside repository:

	if not os.path.exists(AzzPath):
		os.makedirs(AzzPath)

	#~ Open testing / feedback log file:

	azzFileName = 'log' + '_' + time.strftime("%Y%m%d") + '.txt'
	azz = open(AzzPath + '/'+ azzFileName, 'w+')

	print('='*70 + '\n' + 'Starting testing for '+ Stdnt[Hdrs.index('first_name')] + ' ' + Stdnt[Hdrs.index('second_name')] +'\n' + '='*70 + '\n\n')

	azz.write('Starting testing for '+ Stdnt[Hdrs.index('first_name')] + ' ' + Stdnt[Hdrs.index('second_name')] + '\n\n')
	azz.write('Note that: \n')
	azz.write('(1) Major sections begin with a double "====" line \n')
	azz.write('(2) Subsections begin with a single "====" line \n')
	azz.write('(3) Code output or text file content are printed within single "*****" lines \n\n')

	####################################################
	azz.write('='*70 + '\n')
	azz.write('='*70 + '\n')

	azz.write('Your current Git repo size is about ' + RepoStats['size-pack'] +' on disk \n\n')

	azz.write('PART 1: Checking project workflow...\n\n')
	DirCont = os.listdir(RepoPath)
	TempDirs = [name for name in DirCont if os.path.isdir(RepoPath+'/' + name)]
	TempFiles = [name for name in DirCont if os.path.isfile(RepoPath+'/' + name)]
	azz.write('Found the following directories in root directory of repo: '\
	 + ', '.join(TempDirs) + '\n\n')
	azz.write('Found the following files in root directory of repo: '\
	 + ', '.join(TempFiles) + '\n\n')

	#~ Begin testing and logging:
	azz.write('Checking for key files in parent directory...\n\n')
	if '.gitignore' in TempFiles:
		azz.write('Found .gitignore in parent directory, great! \n\n')
		azz.write('Printing contents of .gitignore:\n')
		g = open(RepoPath + '/.gitignore', 'r')
		azz.write('\n' + '*'*70 + '\n')
		for line in g:
			azz.write(line,)
		azz.write('\n' + '*'*70 + '\n\n')
	else:
		azz.write('.gitignore missing!\n\n')
		
	readme = 'n'
	for name in TempFiles:
		if 'readme' in name.lower() and not '~' in name.lower():
			azz.write('Found README in parent directory, named: ' + name + '\n\n')
			azz.write('Printing contents of ' + name + ':' + '\n')
			g = open(RepoPath + '/' + name, 'r')
			azz.write('\n' + '*'*70 + '\n')
			for line in g:
				azz.write(line,)
			azz.write('\n' + '*'*70 + '\n\n')
			readme = 'y'
			break
	if readme == 'n':
		azz.write('README file missing!\n\n')
		
	####################################################
	azz.write('='*70 + '\n')
	azz.write('='*70 + '\n')
	azz.write('PART 2: Checking code and workflow...\n\n')	
	azz.write('='*70 + '\n')

	CodDir = [name for name in TempDirs if 'code' in name.lower()]
	DatDir = [name for name in TempDirs if 'data' in name.lower()]
	ResDir = [name for name in TempDirs if 'result' in name.lower()]
	if not CodDir:
		azz.write('Code directory missing!\n')
		azz.write('Aborting this weeks testing!\n\n')
		break

	if not DatDir: azz.write('Data directory missing!\n\n')

	if not ResDir: 
		azz.write('Results directory missing!\n\n')
		azz.write('Creating Results directory...\n\n')
		os.makedirs(RepoPath+'/Results')
	else:
		ResNames = []
		for root, dirs, files in os.walk(RepoPath + '/' + ResDir[0]):
			for file in files:
				if not file.startswith("."):
					ResNames.append(file)
		if len(ResNames)>0:
			azz.write('Found following files in results directory: ' + ', '.join(ResNames) + '...\n\n')			
			azz.write('Ideally, Results directory should be empty other than, perhaps a .gitkeep. \n\n')
		else:
			azz.write('Results directory is empty - good! \n\n')

	## Now get all code file paths for testing
	Scripts = []
	ScriptNames = []
	for root, dirs, files in os.walk(RepoPath + '/' + CodDir[0]):
		for file in files:
			
			if file.lower().endswith(('.sh','.py','.ipynb','.r','.txt','.bib','.tex')) and not file.startswith(".") :
				Scripts.append(os.path.join(root, file))
				ScriptNames.append(file)

	azz.write('Found ' + str(len(Scripts)) + ' code files: ' + ', '.join(ScriptNames) + '\n\n')

	files = [fname for fname in files if not fname.startswith(".")] # all files except hidden/ghost files
	if len(ScriptNames) < len(files):
		extras = list(set(files) - set(ScriptNames))
		azz.write('Found the following extra (non-code/script) files: ' + ', '.join(extras) + '\n')

	if len(ExpFiles) > 0: # Check if list of expected files was provided
		missing_files = [name for name in ExpFiles if name not in ScriptNames]# Find missing file names
		if len(missing_files) > 0:
			azz.write('The following ' + ({len(missing_files)}) +' files are missing: ' + ', '.join(ResNames) + '...\n\n')
		else: azz.write('All expected code/script files found - good! \n\n')

	## Now test all valid script files that were found
	azz.write('='*70 + '\n')
	azz.write('Testing script/code files...\n\n')
	
	errors = 0 #error counter
	for name in Scripts:
		## cd to current script's directory
		os.chdir(os.path.dirname(name))							
		azz.write('='*70 + '\n')
		azz.write('Inspecting script file ' + os.path.basename(name) + '...\n\n')
		azz.write('File contents are:\n')
		azz.write('\n' + '*'*70 + '\n')
					
		g = open(os.path.basename(name), 'r')
		for line in g:
			azz.write(line,)
		g.close()
		azz.write('\n' + '*'*70 + '\n\n')

		azz.write('Testing ' + os.path.basename(name) + '...\n\n')
		print('Testing ' + os.path.basename(name) + '...\n\n')
					
		if os.path.basename(name).lower().endswith('.sh'):
			p, output, err, time_used = run_popen('bash ' + os.path.basename(name), timeout)
		elif os.path.basename(name).lower().endswith('.py'):
			azz.write(os.path.basename(name) + ' is a Python script file;\n\nchecking for docstrings...\n\n')
			with open(os.path.basename(name)) as f:
				funcs = re.findall(r'def\s.+:',f.read(),re.MULTILINE)
			with open(os.path.basename(name)) as f:
				dstrngs = re.findall(r'"""[\w\W]*?"""',f.read(),re.MULTILINE)
				
				if len(funcs)>0 and len(dstrngs)>0:
					azz.write('Found one or more docstrings and functions\n\n')
					if len(dstrngs) < len(funcs) + 1:
						azz.write('Missing docstring, either in one or functions and/or at the script level\n')
						azz.write('\n')
				elif len(funcs)>0 and len(dstrngs)==0:
					azz.write('Found one or more functions, but completely missing docstrings\n')
				elif len(funcs)==0 and len(dstrngs)==1:
					azz.write('Found no functions, but one docstring for the script, good\n\n')
				elif len(funcs)==0 and len(dstrngs)>2:
					azz.write('Found too many docstrings.  Check your script.\n\n')
				else:
					azz.write('No functions, but no script-level docstring either\n')

			p, output, err,	time_used = run_popen('python3 ' + os.path.basename(name), timeout)
		
		elif os.path.basename(name).lower().endswith('.r'):
			p, output, err,	time_used = run_popen('/usr/lib/R/bin/Rscript ' + os.path.basename(name), timeout)
		else:
			os.chdir(scrptPath)
			continue

		chars = 0
					
		azz.write('Output (only first ' + str(charLim) + ' characters): \n\n')
		azz.write('\n' + '*'*70 + '\n')			 
		for char in output:
			print(char), # use end = '' to removes extra newline in python 3.xx
			subprocess.sys.stdout.flush()
			azz.write(char,)
			chars += 1
			if chars > charLim: # Limit the amount of output
				break
		
		azz.write('\n' + '*'*70 + '\n')
		if not err:
			azz.write('\nCode ran without errors\n\n')
			azz.write('Time consumed = ' +"{:.5f}".format(time_used)+ 's\n\n')
		else:
			errors += 1
			azz.write('\nEncountered error (or warning):\n')
			azz.write('\n***IGNORE IF THIS ERROR IS EXPECTED AS PART OF AN IN-CLASS EXERCISE***\n\n')
			azz.write(err)
			azz.write('\n')
		
		print('\nFinished with ' + os.path.basename(name)+  '\n\n')
		os.chdir(scrptPath)
			
	azz.write('='*70 + '\n')
	azz.write('='*70 + '\n')
	azz.write('Finished running scripts\n\n')
	azz.write('Ran into ' + str(errors)+' errors\n\n')
	
	azz.write('='*70 + '\n')
	azz.write('='*70 + '\n')

	azz.write('Finally, checking git log:\n\n')

	# import ipdb; ipdb.set_trace()
	output = subprocess.check_output(["git","-C", RepoPath, "log"], text=True)

	azz.write(output)

	azz.write('\nFINISHED LOGGING\n\n')

	azz.close()