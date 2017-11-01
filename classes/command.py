#!/usr/bin/python3

import sys
from cmd2 import Cmd, options, make_option

class ShiftShell(Cmd):
	"""
	Command line interface wrapper for Titration
	"""
	intro = "Type help or ? to list commands.\n"
	prompt = ">> "
	file = None
	
	def __init__(self, *args, **kwargs):
		self.allow_cli_args = False
		self.titration = kwargs.get('titration')
		"""
		self.active = self.titration
		self.settable.update({'active' : "Current working titration"})
		"""
		Cmd.__init__(self)
		self.exclude_from_help += ['do__relative_load', 'do_cmdenvironment', 'do_edit', 'do_run']

		complete_save_job=self.path_complete
		complete_load_job=self.path_complete

	def do_save_job(self, arg):
		"Saves active titration to binary file"
		self.titration.save(arg)

	def do_load_job(self, arg):
		"Loads previously saved titration, replacing active titration"
		pass

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
		"""
		if args:
			step = args[0]
		else : 
			step = self.titration.steps -1

		if step == 'all':
			self.titration.plotHistogram()
		else:
			self.titration.plotHistogram(int(step))

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
		split = True if opts.split else False
		if args:
			pass
		else:
			self.titration.plotChemShifts(split=split)

################
##	COMPLETERS
################

	def complete_hist(self, text, line, begidx, endidx):
		"Completer for hist command"
		if text.startswith('--export='):
			text = text.replace('--export=', '')
			return self.path_complete(text, line, begidx, endidx)
		elif text.startswith('--e'):
			return ['--export=']

		histArgs = list( map(str, self.titration.sortedSteps) ) + ['all']
		return self.complete_arg_set(text, line, histArgs)


	def complete_shiftmap(self, text, line, begidx, endidx):
		"Completer for shiftmap command"
		if text.startswith('--export='):
			text = text.replace('--export=', '')
			return self.path_complete(text, line, begidx, endidx)
		elif text.startswith('--e'):
			return ['--export=']

		residueSetArgs = ['all', 'complete', 'filtered', 'selected']
		return self.complete_arg_set(text, line, residueSetArgs)

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