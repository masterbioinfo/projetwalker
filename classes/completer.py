#!/usr/bin/python3

import os
import re
import readline

COMMANDS = {
	"help" : 	None,
	"plot" :	{
		'all' :	None,
		'hist' : [str(x) for x in range(5)],
		'map' : {
			"all": ["split", "global"], 
			"complete" : ["split", "global"], 
			"filtered" : ["split", "global"],
			"selected" : ["split", "global"]
		}
	},
	"save" : 	None,
	"load" : 	None,
	"print": 	list("abcde"),
	"export": 	{
		"map": ['split', 'global'],
		"hist": ['stacked', 'all', 'all_built'] + [str(x) for x in range(5)]
	}
}

COMMANDS['help'] = [ cmd for cmd in COMMANDS if cmd != 'help' ]
RE_SPACE = re.compile(r'.*\s+$', re.M)

"""COMMANDS = ['plot', 'save', 'help', 'load', 'export', 'set', 'print']"""

class Completer(object):
	"""
	Completer class for input() commands
	"""
	def __init__(self):
		self.complete_load = self.complete_arg_path
		self.complete_save = self.complete_arg_path

	def _listdir(self, root):
		"List directory 'root' appending the path separator to subdirs."
		res = []
		for name in os.listdir(root):
			path = os.path.join(root, name)
			if os.path.isdir(path):
				name += os.sep
			res.append(name)
		return res

	def _complete_path(self, path=None):
		"Perform completion of filesystem path."
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

	def complete_arg_path(self, args):
		"Completions for commands having path arguments."
		if not args:
			return self._complete_path('.')
		# treat the last arg as a path and complete it
		return self._complete_path(args[-1])

	def complete_help(self, args):
		"Completions for 'help' command."
		return self.complete_subcommand('help', args)

	def complete_plot(self, args):
		"Completion for 'plot' command."
		return self.complete_subcommand('plot', args)

	def complete_export(self, args):
		"Completion for 'plot' command."
		return self.complete_subcommand('export', args)

	def complete_subcommand(self, cmd, args):
		"""
		Allows completion by iterating over nested subcommand
		"""

		refKey = cmd

		if cmd == 'help': # go through command tree
			refContent = [ cmd for cmd in COMMANDS if cmd != 'help' ]
		else:
			refContent = COMMANDS[cmd]
		
		for arg in args:
			if type(refContent) == dict and refContent.get(arg):
				# Found dict, go deeper
				refKey = arg
				refContent = refContent[arg]
			else:
				break
		#print("++", refKey, refContent,"++")
		if refKey in args[-2:-1] + [cmd] :
			# show possibly matching subcmd
			return [ subcmd + ' ' for subcmd in refContent if subcmd.startswith(args[-1])]
		elif args[-1] == refKey:
			# add space if found exact subcmd match
			return [refKey + ' ']
		else:
			return []

	def complete(self, text, state):
		"Generic readline completion entry point."
		buffer = readline.get_line_buffer()
		line = readline.get_line_buffer().split()

		# show all commands if input is empty
		if not line:
			return [c + ' ' for c in COMMANDS][state]

		# account for last argument ending in a space
		if RE_SPACE.match(buffer):
			line.append('')

		# resolve command to the implementation function
		cmd = line[0].strip()
		if cmd in COMMANDS:
			# complete command args using `impl`
			impl = getattr(self, 'complete_%s' % cmd)
			args = line[1:]
			if args:
				return (impl(args) + [None])[state]
			return [cmd + ' '][state]
		results = [c + ' ' for c in COMMANDS if c.startswith(cmd)] + [None]
		return results[state]

class CommandContainer(object):
	
	def __init__(self, cmdTree = None):
		self.cmds = dict()
		if cmdTree:
			for cmd, subTree in cmdTree.items():
				self.add_command(cmd, subTree)
				
	def add_command(self, cmd, **kwargs):
		"""
		Add or replace command
		kwargs are CommandMapper __init__ kwargs
		"""
		if cmdTree:
			self.cmds[cmd] = CommandMapper(cmd, **kwargs)

	def execute(self, cmdLine):
		cmdParse = cmdLine.strip().split()

		help = [ helpFlag for helpFlag in cmdParse if helpFlag in ('-h', '--help') ]
		for helpFlag in help : cmdParse.remove(helpFlag)

		cmdNode = self.cmds.get(cmdParse[0])
		if cmdNode:
			cmd, args = cmdNode.get_subcommand(cmdParse[1:])
			cmd.execute(args)


class CommandMapper(object):
	def __init__(self, cmd, cmdTree = None, func = None, args = None,
				help = None, parent = None, subCmds = None):
		
		self.cmd = cmd # command name
		self.subs = dict()

		if cmdTree:
			self.parse_branch(cmdTree)

		# kwargs merge with cmdTree data when possible, or overwrite
		self.help = help or self.help # overwrite
		self.parent = parent
		self.func = func or self.func # overwrite
		if args : # merge
			self.args.update(args)

		if type(subCmds) == list: # merge (replacing)
			# as a list of CommandMapper objects
			for subCmd in subCmds:
				self.subs[subCmd.cmd] = subCmd
		elif type(subCmds) == dict:
			# as a command tree dict
			self.parse_branch(subCmds)
		

	def parse_tree(self, tree):
		"Parse command descriptor tree"
		self.help = tree.get['help']
		self.func = tree.get('func')
		self.args = tree.get('args')
		if tree.get('subs'):
			self.parse_branch(tree['subs'])

	def parse_branch(self, branch):
		"Parses subcommands branch"
		for subCmd, subBranch in branch.items():
			self.add_subcommand(subCmd, subBranch)

	def add_subcommand(self, cmd, **kwargs):
		""""
		Add or replace subcommand
		kwargs are CommandMapper __init__ kwargs
		"""
		self.subCmds[cmd] = CommandMapper(cmd, parent=self, **kwargs)
		return self.subs[cmd]

	def get_subcommand(self, cmd):
		if type(cmd) == str:
			cmd = cmdLine.strip().split()
		subCmd = self.subs.get(cmd[0])
		if subCmd:
			return subCmd.get_subcommand(cmd[1:])
		else:
			args = cmd
			return self, args

	def execute(self, args=[] ):
		if args :
			for arg in args:
				arg = self.args.get(arg) or arg
			return self.func(*args)
		else:
			return self.func()

"""
Usage
comp = Completer()
# we want to treat '/' as part of a word, so override the delimiters
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(comp.complete)
raw_input('Enter section name: ')

"""
