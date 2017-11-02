#!/usr/bin/python3

import sys, os
from cmd2 import Cmd, options, make_option

class ShiftShell(Cmd):
	"""
	Command line interface wrapper for Titration
	"""
	intro = "Type help or ? to list commands.\n"
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

		# Exclude irrelevant cmds from help menu
		self.exclude_from_help += ['do__relative_load', 'do_cmdenvironment', 'do_edit', 'do_run']

		# Set path completion for save/load
		self.complete_save_job=self.path_complete
		self.complete_load_job=self.path_complete

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
			hist = self.titration.plotHistogram()
		else: # plot single hist
			hist = self.titration.plotHistogram(step=int(step))
		
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
		if args:
			pass # parse arguments here
		else:
			fig = self.titration.plotChemShifts(split=opts.split)
		if opts.export:
			fig.savefig(opts.export, dpi=fig.dpi)

	def do_extract_residues(self, arg):
		self.titration.extractResidues()


	@options([
		make_option('-p', '--plot', action="store_true", help="Set cut-off and plot.")
	],
	arg_desc = '<float>')
	def do_cutoff(self, args, opts=None):
		try:
			cutOff = float(args[0])
			self.titration.setCutOff(cutOff)
		except (TypeError, IndexError):
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
