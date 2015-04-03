import os
import shutil
import hashlib

class Syncer(object):
	'''Takes a list of iterables with each two members of the form
	(src_dir, dst_dir).'''
	def __init__(self, mapping_tuples):
		self.mapping_tuples = mapping_tuples

	@staticmethod
	def _remove_path_prefix(file_path, prefix):
		path_parts   = file_path.split(os.sep)
		prefix_parts = prefix.split(os.sep)
		for p in prefix_parts:
			# If this assertion fails, it means the prefix wasn't really part
			# of the file path
			assert p == path_parts.pop(0)

		# Now path_parts is all that is left of the file
		return os.sep.join(path_parts)

	@staticmethod
	def _get_files_src_dst(src_base, dst_base):
		files_to_sync = []
		for root, dirs, files in os.walk(src_base):
			for f in files:
				file_no_root = Syncer._remove_path_prefix(os.path.join(root,f), src_base)
				src_file = os.path.join(src_base, file_no_root)
				dst_file = os.path.join(dst_base, file_no_root)
				files_to_sync.append((src_file, dst_file))
		return files_to_sync

	@staticmethod
	def _get_all_files(base):
		all_files = []
		for root, dirs, files in os.walk(base):
			for f in files:
				all_files.append(os.path.join(root,f))
		return all_files

	def get_all_destination_files(self):
		destination_files = []
		for t in self.mapping_tuples:
			dst_base = t[1]
			destination_files.extend(Syncer._get_all_files(dst_base))
		return destination_files

	def get_files_to_sync(self):
		'''Based on te mapping tuples provided in the init function, returns a
		list of tuples of the form (src_file, src_dir)'''
		files_to_sync = []
		for t in self.mapping_tuples:
			(src_base, dst_base) = t[0], t[1]
			files_to_sync.extend(
				Syncer._get_files_src_dst(src_base, dst_base)
				)
		return files_to_sync

	def sync(self, delete_dst_only_files):
		# A big list of (src,dst)
		files_to_sync = self.get_files_to_sync()

		# All destination directories should exist
		dirs_to_create = []
		# Find all the dirs what need creating
		for src, dst in files_to_sync:
			d = os.path.split(dst)[0]
			if d not in dirs_to_create:
				dirs_to_create.append(d)
		# Create them all
		for d in dirs_to_create:
			try:
				os.makedirs(d)
			except:
				pass

		# Destination files which are not in the source.. should they exist?
		if delete_dst_only_files:
			destination_files = self.get_all_destination_files()
			files_which_should_be_in_destination = zip(*files_to_sync)[1]

			for d in destination_files:
				if not d in files_which_should_be_in_destination:
					print 'Deleting',d
					os.remove(d)

		# Now copy the files over if they're not the same already. This is
		# probably slower than just always copying them
		for src, dst in files_to_sync:
			assert os.path.exists(src)
			if os.path.exists(dst):
				if hashlib.md5(open(src).read()).hexdigest() == hashlib.md5(open(dst).read()).hexdigest():
					continue
			print 'Copying',src,'to',dst
			shutil.copy(src, dst)
