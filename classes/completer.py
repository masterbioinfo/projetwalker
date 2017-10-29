#!/usr/bin/python3

import os
import re
import readline

COMMANDS = {
	"save" : None,
	"help" : None,
	"load" : None,
	"print": list("abcde")
}
COMMANDS['help'] = [ cmd for cmd in COMMANDS if cmd != 'help' ]
"""
COMMANDS = ['plot', 'save', 'help', 'load',
			'export', 'set', 'print']
"""
RE_SPACE = re.compile('.*\s+$', re.M)

print(COMMANDS)
class Completer(object):
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

	def complete_subcommand(self, cmd, args):
		"""
		Allows completion by iterating over nested subcommand
		"""
		if cmd == 'help':
			ref = COMMANDS
		else:
			ref = COMMANDS[cmd]
		lastRefName = cmd
		for arg in args:
			if type(ref) == dict and ref.get(arg):
				# Found dict, go deeper
				lastRefName = arg
				ref = ref[arg]
			else:
				break
		if lastRefName in args[-2:-1] + [cmd] :
			return [ subcmd + ' ' for subcmd in ref if subcmd.startswith(args[-1])]
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



"""
Usage
comp = Completer()
# we want to treat '/' as part of a word, so override the delimiters
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(comp.complete)
raw_input('Enter section name: ')

"""