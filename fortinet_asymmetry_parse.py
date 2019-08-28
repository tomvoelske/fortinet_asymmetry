#!usr/bin/env python
import datetime
import os
import re
import sys
sys.path.append('/anonymised/path')
import jsoncommands


def parse(todaydate):

	# important variables

	rootdir = '/anonymised/path/' + todaydate + '/'
	reportroot = '/anonymised/path/'
	relevantpattern = '(\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})[@](\d+)[(]?([\w._-]*)[)]?->(\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})[@](\d+)[(]?([\w._-]*)[)]?'
	datadict = {}
	outputloc = '/anonymised/path/asymmetry_data.json'

	datafiles = os.listdir(rootdir)

	for datafile in datafiles:
		hostvdom = datafile.replace('.txt', '')
		datapath = rootdir + datafile
		reportpath = reportroot + hostvdom + '-asym.txt'

		with open(datapath, 'r') as testfile:
			testarray = testfile.readlines()

		matcharray = []
		matchesprocessed = []
		asymmetricarray = []
		asymmetric = 0
		symmetric = 0
		duplicates = 0
		unpaired = 0
		blanks = 0

		print('FILE: ' + datafile)

		for testline in testarray:
			regextest = re.search(relevantpattern, testline, re.IGNORECASE)
			if regextest:
				matchadd = []
				for x in range(1, 7):
					# ip, port (@n), intf (human name) ~ ip, port (@n), intf (human name)
					matchadd.append(regextest.group(x))
				matcharray.append(matchadd)

		while len(matcharray) > 0:

			# using while instead of for as we remove elements from the array as we go on, so length needs to be
			# recalculated each loop, until the array is empty
			# removed elements are most current (highest index) and any matched pair (lower index)

			#print('{0} elements to go...'.format(len(matcharray)))

			matchfound = False
			blankinterface_relevant = False

			relevantarray = matcharray.pop()
			relevantipa = relevantarray[0]
			relevantporta = relevantarray[1]
			relevantintfa = relevantarray[2]
			if not relevantintfa:
				relevantintfa = "(BLANK)"
				blankinterface_relevant = True
			relevantipb = relevantarray[3]
			relevantportb = relevantarray[4]
			relevantintfb = relevantarray[5]
			if not relevantintfb:
				relevantintfb = "(BLANK)"
				blankinterface_relevant = True
			characteristicreference = relevantipa + relevantipb

			if characteristicreference in matchesprocessed:
				duplicates += 1
				continue

			for checkindex, checkarray in enumerate(matcharray):

				blankinterface_test = False

				testipa = checkarray[0]
				testporta = checkarray[1]
				testintfa = checkarray[2]
				if not testintfa:
					testintfa = "(BLANK)"
					blankinterface_test = True
				testipb = checkarray[3]
				testportb = checkarray[4]
				testintfb = checkarray[5]
				if not testintfb:
					testintfb = "(BLANK)"
					blankinterface_test = True

				if relevantipa == testipb and relevantipb == testipa:

					matchfound = True

					if relevantporta == testportb and relevantportb == testporta:
						# symmetric
						symmetric += 1
						del matcharray[checkindex]

					else:

						if blankinterface_relevant or blankinterface_test:
							blanks += 1

						elif relevantportb != testporta:
							# straightforward asymmetric
							asymmetricstring = '{0} [interface {1} @{2}] -> {3}'.format(relevantipa, relevantintfa,
																						relevantporta, relevantipb)
							asymmetricstring += ' [interface {0} @{1}], returning on [interface {2} @{3}]'.format(relevantintfb,
																										  relevantportb,
																										  testintfa,
																										  testporta)
						elif relevantporta != testportb:
							# reverse asymmetric
							asymmetricstring = '{0} [interface {1} @{2}] -> {3}'.format(relevantipb, relevantintfb,
																						relevantportb, testipb)
							asymmetricstring += ' [interface {0} @{1}], returning on [interface {2} @{3}]'.format(testintfb,
																										  testportb,
																										  relevantintfa,
																										  relevantporta)
						else:
							print('ERROR')

						if not blankinterface_relevant and not blankinterface_test:

							if not asymmetricstring in asymmetricarray:
								asymmetric += 1
								asymmetricarray.append(asymmetricstring)
							else:
								duplicates += 1

						del matcharray[checkindex]

					break

			if not matchfound:
				unpaired += 1

			matchesprocessed.append(characteristicreference)

		if asymmetric > 0:

			with open(reportpath, 'w') as resultfile:
				for asymindex, asymmetriclines in enumerate(asymmetricarray):
					linetowrite = "FLOW " + str(asymindex + 1) + ": " + asymmetriclines + "\n"
					print(linetowrite)
					resultfile.write(linetowrite)

		print('ASYMMETRIC: ' + str(asymmetric))
		print('SYMMETRIC: ' + str(symmetric))
		print('DUPLICATES: ' + str(duplicates))
		print('UNPAIRED: ' + str(unpaired))
		print('BLANKS: ' + str(blanks))

		datadict[hostvdom] = {'asymmetric': asymmetric, 'symmetric': symmetric, 'duplicates': duplicates,
							  'unpaired': unpaired, 'blank': blanks}

		os.remove(datapath)
	os.rmdir(rootdir)

	datadict['polltime'] = datetime.datetime.today().strftime('%d/%m/%Y')
	jsoncommands.writejson(datadict, outputloc)


if __name__ == '__main__':
	parse(datetime.datetime.today().strftime('%d%m%Y'))
