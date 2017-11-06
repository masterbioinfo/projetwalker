#!/usr/bin/python3

import sys, os
from cmd2 import Cmd, options, make_option

class ShiftShell(Cmd):
	"""
	Command line interface wrapper for Titration
	"""
	intro = "Welcome to Shift2Me !\n"\
			"Type help or ? to list commands.\n"
	prompt = ">> "
	file = None
	cutOff = None
	
	def __init__(self, *args, **kwargs):
		self.allow_cli_args = False
		self.titration = kwargs.get('titration')
		
		"""
		self.active = self.titration
		self.settable.update({'active' : "Current working titration"})
		"""
		Cmd.__init__(self)
		self._set_prompt()

		# Exclude irrelevant cmds from help menu
		self.exclude_from_help += ['do__relative_load', 'do_cmdenvironment', 'do_edit', 'do_run']

		# Set path completion for save/load
		self.complete_save_job=self.path_complete
		self.complete_load_job=self.path_complete
		self.complete_add_step=self.path_complete

		self.intro = self.titration.summary + "\n"+ self.intro

	def _set_prompt(self):
		"""Set prompt so it displays the current working directory."""
		self.cwd = os.getcwd().strip("'")
		self.prompt = self.colorize("[shift2me]", 'magenta') + " >> "

	@options([],arg_desc='<titration_file_##.list>')
	def do_add_step(self, arg, opts=None):
		"Add a titration file as next step"
		self.titration.add_step(arg[0])

	def do_save_job(self, arg):
		"Saves active titration to binary file"
		self.titration.save(arg)

	def do_load_job(self, arg):
		"Loads previously saved titration, replacing active titration"
		self.titration.load(arg)

	def do_new(self, arg):
		"""
		Creates a new titration from either : 
		 - a dir containing .list files
		 - a list of .list files
		 - a binary file of previously saved titration
		"""
		pass


	@options([make_option('-e', '--export', help="Export hist as image")],
			arg_desc='(<titration_step> | all)')
	def do_hist(self, args, opts=None):
		"""
		Plot chemical shift intensity per residu as histograms
		Accepted arguments are any titration step except 0 (reference)
		or 'all' to plot all steps as stacked histograms. 
		Defaults to plotting the last step when no arguments
		are provided.
		"""
		step = args[0] if args else self.titration.steps -1
		if step == 'all': # plot stacked hist
			hist = self.titration.plot_hist()
		else: # plot single hist
			hist = self.titration.plot_hist(step=int(step))
		
		if opts.export: # export figure as png
			hist.figure.savefig(opts.export, dpi = hist.figure.dpi)


	@options([
		make_option('-s', '--split', action="store_true", help="Sublot each residue individually."),
		make_option('-e', '--export', help="Export 2D shifts map as image")
	],
	arg_desc='( all | complete | filtered | selected )')
	def do_shiftmap(self, args, opts=None):
		"""
		Plot chemical shifts for H and N atoms for each residue at each titration step.
		Invocation with no arguments will plot all residues with complete data.
		"""
		try:
			if args:
				fig = self.titration.plot_shiftmap(args[0], split=opts.split)
			else:
				fig = self.titration.plot_shiftmap(split=opts.split)
			if opts.export:
				fig.savefig(opts.export, dpi=fig.dpi)
		except ValueError as invalidArgErr:
			sys.stderr.write("%s\n" % invalidArgErr)
			self.do_help("shiftmap")
			self.stdout.write("")

	@options([], arg_desc="( filtered | selected | complete | incomplete )")
	def do_print(self, args, opts=None):
		"Output specific titration infos to standard output"
		argMap = {
			"filtered" : self.titration.filtered,
			"selected" : self.titration.selected,
			"complete" : self.titration.complete,
			"incomplete" : self.titration.incomplete
		}
		for arg in args:
			try:
				if arg in argMap:
					self.stdout.write("%s\n" % " ".join([str(pos) for pos in argMap[arg]]))
				else:
					raise ValueError("Skipping invalid argument %s" % arg)
			except ValueError as error:
				sys.stderr.write("%s\n" % error)
				pass


	@options([])
	def do_filter(self, args, opts=None):
		"Output residues having intensity >= cut-off"
		self.stdout.write("%s\n" % " ".join([str(pos) for pos in self.titration.filtered]))


	@options([], arg_desc="[all] [filtered] [complete] [incomplete] [positions_slice]")
	def do_select(self, args, opts=None):
		"""
		Select a subset of residues, either from : 
		 - a predefined set of residues
		 - 1 or more slices of residue positions, with python-ish syntax.
		Examples : 
			':100' matches positions from start to 100
			'110:117' matches positions from 100 to 117 (excluded)
			'105 112:115' matches positions 105 and 112 to 115 (excluded)
		You may mix argument types, like select filtered residues + res #100 to #110 excluded :
			>> select filtered 100:110
		Non existant residues are skipped with a warning message.
		Finally, selection is additive only, each selected element adds up to previous selection. 
		If you want to clear the current selection, use deselect command.
		"""
		argMap = {
			"all" : self.titration.residues,
			"filtered" : self.titration.filtered,
			"complete" : self.titration.complete,
			"incomplete" : self.titration.incomplete
		}
		selection = []
		for arg in args:
			if arg in argMap:
				args.remove(arg)
				selection += list(argMap[arg])

		selection += self.parse_residue_slice(args)
		self.titration.select_residues(*selection)


	@options([])
	def do_deselect(self, args, opts=None):
		"""
		Remove a subset of residues from current selection, specifying either : 
		 - a predefined set of residues
		 - 1 or more slices of residue positions, with python-ish syntax.
		   e.g : ':100' matches positions from start to 100
		         '110:117' matches positions from 100 to 117 (excluded)
				 '105 112:115' matches positions 105 and 112 to 115 (excluded)
		You may mix argument types, like deselect filtered residues + res #100 to #110 excluded :
			>> deselect filtered 100:110
		Deselection will silently ignore on currently non-selected residue.
		"""
		argMap = {
			"all" : self.titration.residues,
			"filtered" : self.titration.filtered,
			"complete" : self.titration.complete,
			"incomplete" : self.titration.incomplete
		}
		selection = []
		for arg in args:
			if arg in argMap:
				args.remove(arg)
				selection += list(argMap[arg])
		selection += self.parse_residue_slice(args)
		self.titration.deselect_residues(*selection)

	def parse_residue_slice(self, sliceList):
		"""
		Parses a list of residue position slices
		a list element might describe an arbitrary of ';' separated slices
		slices are expanded the same as python slice, i.e 5:8 will yield 5,6,7
		5: will yield all positions from 5 to last.
		"""
		selection = []
		for mainArg in sliceList:
			altSplitArg = mainArg.split(';')
			for arg in altSplitArg:
				arg = arg.split(':')
				arg = [ int(subArg) if subArg else None for subArg in arg]
				if len(arg) > 1:
					if all(subArg is None for subArg in arg):
						break
					elif arg[0] is None:
						selection += range(min(self.titration.residues), arg[1])
					elif arg[1] is None:
						selection += range(arg[0], max(self.titration.residues))
					else:
						selection += range(arg[0], arg[1])
				elif len(arg) == 1:
					selection += arg
				else:
					break
		return selection

	def do_summary(self, args):
		"Prints a summary of current titration state"
		self.stdout.write("%s" % self.titration.summary)

	@options([
		make_option('-p', '--plot', action="store_true", help="Set cut-off and plot.")
	],
	arg_desc = '<float>')
	def do_cutoff(self, args, opts=None):
		try:
			print(args)
			if not args :
				self.stdout.write("Cut-off=%s\n" % self.titration.cutOff)
			else:
				cutOff = float(args[0])
				self.titration.set_cutoff(cutOff)
			if opts.plot:
				self.titration.plot_hist(-1)
		except (TypeError, IndexError) as error:
			sys.stderr.write("%s\n" % error)
			self.do_help("cutoff")


################
##	COMPLETERS
################

	def complete_hist(self, text, line ,begidx, endidx):
		"Completer for hist command"
		flagComplete = self.complete_flag_path('e', 'export', text, line ,begidx, endidx)
		if flagComplete: return flagComplete

		histArgs = list( map(str, self.titration.sortedSteps) ) + ['all']
		return self.complete_arg_set(text, line, histArgs)


	def complete_shiftmap(self, text, line ,begidx, endidx):
		"Completer for shiftmap command"
		flagComplete = self.complete_flag_path('e', 'export', text, line ,begidx, endidx)
		if flagComplete: return flagComplete

		residueSetArgs = ['all', 'complete', 'filtered', 'selected']
		return self.complete_arg_set(text, line, residueSetArgs)

	def complete_print(self, text, line ,begidx, endidx):
		"Completer for shiftmap command"
		residueSetArgs = ['incomplete', 'complete', 'filtered', 'selected']
		return self.complete_arg_set(text, line, residueSetArgs)

	def complete_flag_path(self, shortFlag, longFlag, text, line ,begidx, endidx):
		# accept --flag=, flag=, --flag, flag
		longFlag = '--'+longFlag.strip('--=')+'='
		shortFlag = '-'+shortFlag.strip('-')
		if text.startswith(longFlag):
			# remove flag and start path completion
			pathText = text[len(longFlag):]
			return [longFlag + path for path in self._complete_truncated(pathText) ]
			
			# complete flag (this is ugly if several flags start with same letter)
		elif text.startswith(longFlag[:3]):
			return [longFlag]
		return []

	def complete_select(self, text, line ,begidx, endidx):
		"Completer for select command"
		residueSetArgs = ['incomplete', 'complete', 'filtered', 'all']
		return self.complete_arg_set(text, line, residueSetArgs)

	def complete_deselect(self, text, line ,begidx, endidx):
		return self.complete_select(text, line ,begidx, endidx)

	def _listdir(self, root):
		"List directory 'root' appending the path separator to subdirs."
		res = []
		for name in os.listdir(root):
			path = os.path.join(root, name)
			if os.path.isdir(path):
				name += os.sep
			res.append(name)
		return res

	def _complete_truncated(self, path=None):
		"Perform completion of filesystem path when inside a posix flag"
		if not path:
			return self._listdir('.')
		dirname, rest = os.path.split(path)
		tmp = dirname if dirname else '.'
		res = [os.path.join(dirname, p)
				for p in self._listdir(tmp) if p.startswith(rest)]
		# more than one match, or single match which does not exist (typo)
		if len(res) > 1 or not os.path.exists(path):
			return res
		# resolved to a single directory, so return list of files below it
		if os.path.isdir(path):
			return [os.path.join(path, p) for p in self._listdir(path)]
		# exact file match terminates this completion
		return [path + ' ']

	def complete_arg_set(self, text, line, argSet):
		"Completion logic for commands accepting predefined set of arguments"
		# Last word is an exact match with args
		if text in argSet:
			return [text+' '] 
		# Arg already provided
		for arg in argSet:
			if arg in line.split():
				return []
		# Arg matches with many allowed args
		return [ arg+' ' for arg in argSet if arg.startswith(text) ]
