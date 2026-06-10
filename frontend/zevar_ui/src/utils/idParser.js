/**
 * AAMVA Driver's License / ID Card Parser
 *
 * Parses PDF417 barcode data conforming to the AAMVA standard (versions 2000–2016+).
 * Handles edge cases: mixed line endings (\r\n, \r, \n), missing whitespace,
 * concatenated subfile designators, and version-specific field layouts.
 */

// Known 3-character AAMVA field codes used as delimiters during greedy capture.
// Not exhaustive — only the codes we extract plus common surrounding ones.
const FIELD_CODES = [
	'DAQ',
	'DCS',
	'DAC',
	'DCT',
	'DAD',
	'DBA',
	'DBB',
	'DBC',
	'DBD',
	'DAY',
	'DAG',
	'DAI',
	'DAJ',
	'DAK',
	'DAL',
	'DAM',
	'DCG',
	'DCS',
	'DAB',
	'DAU',
	'DCA',
	'DCB',
	'DCD',
	'DDE',
	'DDF',
	'DDG',
	'DDH',
	'DDI',
	'DDJ',
	'DDK',
	'DDL',
	'DAA',
	'DAB',
	'DAC',
	'DAD',
	'DAE',
	'DAF',
	'DAG',
	'DAH',
	'DAI',
	'DAJ',
	'DAK',
	'DAL',
	'DAM',
	'DCE',
	'DCF',
	'DCG',
	'DCH',
	'DCI',
	'ZG',
	'ZI',
	'ZJ',
	'ZK',
	'ZL',
	'ZM',
	'ZN',
	'ZO',
]

const FIELD_CODE_SET = new Set(FIELD_CODES)

/**
 * Detect whether raw scan data follows the AAMVA standard.
 */
export function isAAMVA(data) {
	if (!data || typeof data !== 'string') return false
	// AAMVA data always starts with '@@' or 'ANSI ' or contains known subfile markers
	return data.startsWith('@@') || /^\s*ANSI\s/.test(data) || data.includes('DAQ')
}

/**
 * Normalize line endings: convert \r\n and \r to \n, then collapse multiple spaces.
 */
function normalize(data) {
	return data.replace(/\r\n/g, '\n').replace(/\r/g, '\n')
}

/**
 * Greedy field extractor.
 *
 * Finds `code` in the normalized data and captures everything after it
 * until the next known AAMVA field code (preceded by a newline) or end of string.
 * This handles missing whitespace and concatenated fields like "DAQ12345678DCSSMITH".
 */
function getField(data, code) {
	const startIdx = data.indexOf(code)
	if (startIdx === -1) return ''

	const valueStart = startIdx + code.length
	let valueEnd = data.length

	// Scan forward from the value start, looking for the next known field code
	for (let i = valueStart; i < data.length - 2; i++) {
		const candidate = data.substring(i, i + 3)
		if (FIELD_CODE_SET.has(candidate)) {
			// Only treat as a delimiter if preceded by nothing (concatenated)
			// or by a newline/whitespace boundary. If whitespace is missing,
			// AAMVA concatenates fields directly, so we just check the code.
			const prevChar = data[i - 1]
			if (
				i === valueStart ||
				prevChar === '\n' ||
				prevChar === ' ' ||
				/^[A-Z0-9]$/.test(prevChar) ||
				!prevChar
			) {
				valueEnd = i
				break
			}
		}
	}

	// Trim trailing whitespace/newlines from the captured value
	return data.substring(valueStart, valueEnd).trim()
}

/**
 * Parse DOB from AAMVA DBB field.
 *
 * AAMVA stores DOB in MMDDYYYY format (most common) or sometimes YYYYMMDD.
 * We detect the format based on the first two digits.
 */
function parseDOB(rawDob) {
	if (!rawDob || rawDob.length < 8) return ''

	// Remove any non-digit characters
	const digits = rawDob.replace(/\D/g, '')
	if (digits.length < 8) return ''

	let year, month, day
	const firstTwo = parseInt(digits.substring(0, 2), 10)

	if (firstTwo === 19 || firstTwo === 20) {
		// YYYYMMDD format
		year = digits.substring(0, 4)
		month = digits.substring(4, 6)
		day = digits.substring(6, 8)
	} else {
		// MMDDYYYY format (AAMVA standard)
		month = digits.substring(0, 2)
		day = digits.substring(2, 4)
		year = digits.substring(4, 8)
	}

	return `${year}-${month}-${day}`
}

/**
 * Parse a full AAMVA string into structured data.
 *
 * @param {string} data - Raw PDF417 scan data
 * @returns {{ name: string, firstName: string, lastName: string, address: string, city: string, state: string, zip: string, dob: string, idNumber: string, type: string }}
 */
export function parseAAMVA(data) {
	const result = {
		name: '',
		firstName: '',
		lastName: '',
		address: '',
		city: '',
		state: '',
		zip: '',
		dob: '',
		idNumber: '',
		type: 'drivers_license',
	}

	if (!data) return result

	const normalized = normalize(data)

	// Name fields — DCS = last name, DAC/DCT = first name, DAD = middle
	const lastName = getField(normalized, 'DCS') || getField(normalized, 'DAB') || ''
	const firstName = getField(normalized, 'DAC') || getField(normalized, 'DCT') || ''
	const middleName = getField(normalized, 'DAD') || ''

	result.firstName = firstName
	result.lastName = lastName

	const nameParts = [firstName, middleName, lastName].filter(Boolean)
	result.name = nameParts.join(' ')

	// Address fields
	const street = getField(normalized, 'DAG') || ''
	const city = getField(normalized, 'DAI') || ''
	const state = getField(normalized, 'DAJ') || ''
	const zip = getField(normalized, 'DAK') || ''

	result.address = street
	result.city = city
	result.state = state
	result.zip = zip.substring(0, 5)

	// Date of birth — DBB field
	const rawDob = getField(normalized, 'DBB')
	result.dob = parseDOB(rawDob)

	// ID / Document Number — DAQ field
	result.idNumber = getField(normalized, 'DAQ')

	return result
}

/**
 * Detect whether raw scan data represents an Indian Aadhaar card.
 */
export function isAadhaar(data) {
	if (!data || typeof data !== 'string') return false
	return (
		data.includes('<PrintLetterBarcodeData') ||
		data.includes('PrintLetterBarcodeData') ||
		data.includes('Aadhaar') ||
		/uid="\d{12}"/i.test(data)
	)
}

/**
 * Parse an Aadhaar card XML QR code or text structure.
 */
export function parseAadhaar(data) {
	const result = {
		name: '',
		firstName: '',
		lastName: '',
		address: '',
		city: '',
		state: '',
		zip: '',
		dob: '',
		idNumber: '',
		type: 'national_id',
	}

	if (!data) return result

	// Get attribute helper
	const getAttr = (attr) => {
		const match = data.match(new RegExp(`${attr}="([^"]*)"`, 'i'))
		return match ? match[1].trim() : ''
	}

	if (data.includes('PrintLetterBarcodeData')) {
		const uid = getAttr('uid')
		const name = getAttr('name')
		const dob = getAttr('dob')
		const yob = getAttr('yob')
		const house = getAttr('house')
		const street = getAttr('street')
		const lm = getAttr('lm')
		const vtc = getAttr('vtc')
		const po = getAttr('po')
		const dist = getAttr('dist')
		const state = getAttr('state')
		const pc = getAttr('pc')

		result.idNumber = uid
		result.name = name

		if (name) {
			const parts = name.split(/\s+/)
			if (parts.length > 1) {
				result.lastName = parts.pop()
				result.firstName = parts.join(' ')
			} else {
				result.firstName = name
				result.lastName = ''
			}
		}

		const addrParts = [house, street, lm, vtc, po, dist].filter(Boolean)
		result.address = addrParts.join(', ')
		result.city = vtc || dist || ''
		result.state = state
		result.zip = pc

		if (dob) {
			result.dob = parseAadhaarDOB(dob)
		} else if (yob) {
			result.dob = `${yob}-01-01`
		}
	} else {
		// Fallback for simple plain text QR codes / text scans
		const uidMatch = data.match(/\b\d{4}\s?\d{4}\s?\d{4}\b/)
		if (uidMatch) {
			result.idNumber = uidMatch[0].replace(/\s/g, '')
		}

		const dobMatch = data.match(/dob\s*:\s*(\d{2}[-/]\d{2}[-/]\d{4})/i)
		if (dobMatch) {
			result.dob = parseAadhaarDOB(dobMatch[1])
		}

		const nameMatch = data.match(/name\s*:\s*([^\n,]+)/i)
		if (nameMatch) {
			const nameVal = nameMatch[1].trim()
			result.name = nameVal
			const parts = nameVal.split(/\s+/)
			if (parts.length > 1) {
				result.lastName = parts.pop()
				result.firstName = parts.join(' ')
			} else {
				result.firstName = nameVal
			}
		}

		const stateMatch = data.match(/state\s*:\s*([^\n,]+)/i)
		if (stateMatch) result.state = stateMatch[1].trim()

		const pcMatch = data.match(/\b\d{6}\b/)
		if (pcMatch) result.zip = pcMatch[0]
	}

	return result
}

function parseAadhaarDOB(dobStr) {
	if (!dobStr) return ''
	const cleanDob = dobStr.replace(/\//g, '-')
	const parts = cleanDob.split('-')
	if (parts.length === 3) {
		if (parts[2].length === 4) {
			return `${parts[2]}-${parts[1]}-${parts[0]}`
		}
		if (parts[0].length === 4) {
			return cleanDob
		}
	}
	return cleanDob
}

/**
 * Parse raw OCR text from an ID/Aadhaar card into structured fields.
 */
export function parseOCRText(text) {
	const result = {
		name: '',
		firstName: '',
		lastName: '',
		address: '',
		city: '',
		state: '',
		zip: '',
		dob: '',
		idNumber: '',
		type: 'national_id',
	}

	if (!text) return result

	// 1. Extract ID/DL number — try multiple patterns
	const dlPatterns = [
		/(?:4d\s*)?DLN\s*([A-Z0-9]{5,14})/i, // AAMVA 4d DLN prefix
		/DL\s*(?:NO|#|:)?\s*([A-Z0-9]{5,14})/i, // DL NO / DL# / DL:
		/(?:LICENSE|LIC)\s*(?:NO|#|:)?\s*([A-Z0-9]{5,14})/i, // LICENSE NO
		/(?:ID)\s*(?:NO|#|:)?\s*([A-Z0-9]{5,14})/i, // ID NO
		/\b([A-Z]\d{7,13})\b/, // California format: letter + 7-13 digits
		/\b(\d{3}-\d{2}-\d{4})\b/, // SSN format (some states)
	]
	for (const pat of dlPatterns) {
		const m = text.match(pat)
		if (m) {
			result.idNumber = m[1].replace(/\s/g, '')
			break
		}
	}
	// Aadhaar fallback
	if (!result.idNumber) {
		const uidMatch = text.match(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/)
		if (uidMatch) result.idNumber = uidMatch[0].replace(/[\s-]/g, '')
	}

	// 2. Extract DOB — try labeled then bare date patterns
	const dobPatterns = [
		/(?:DOB|D\.?O\.?B|BIRTH|DATE\s*OF\s*BIRTH)\s*[:.]?\s*(\d{1,2}[\s/.-]\d{1,2}[\s/.-]\d{2,4})/i,
		/\b3\s+DOB\s+(\d{1,2}[/.-]\d{1,2}[/.-]\d{4})\b/i, // AAMVA field 3 DOB
	]
	let rawDob = ''
	for (const pat of dobPatterns) {
		const m = text.match(pat)
		if (m) {
			rawDob = m[1]
			break
		}
	}
	// Fallback: find any MM/DD/YYYY date
	if (!rawDob) {
		const dateMatch = text.match(/\b(\d{1,2}[/.-]\d{1,2}[/.-]\d{4})\b/)
		if (dateMatch) rawDob = dateMatch[1]
	}
	if (rawDob) {
		const cleanDob = rawDob.replace(/[/.]/g, '-').replace(/\s/g, '')
		const parts = cleanDob.split('-')
		if (parts.length === 3 && parts[2].length === 4) {
			const p0 = parseInt(parts[0], 10)
			if (p0 > 12) {
				result.dob = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(
					2,
					'0'
				)}`
			} else {
				result.dob = `${parts[2]}-${parts[0].padStart(2, '0')}-${parts[1].padStart(
					2,
					'0'
				)}`
			}
		} else if (parts.length === 3 && parts[0].length === 4) {
			result.dob = `${parts[0]}-${parts[1].padStart(2, '0')}-${parts[2].padStart(2, '0')}`
		}
	}

	// 3. Extract Name — multiple strategies
	const linesRaw = text
		.split('\n')
		.map((line) => line.trim())
		.filter((line) => line.length > 1)

	// Strategy A: Look for AAMVA visual field numbers (1 LASTNAME, 2 FIRSTNAME)
	let aamvaLastName = ''
	let aamvaFirstName = ''
	let aamvaAddress = []

	for (let i = 0; i < linesRaw.length; i++) {
		const line = linesRaw[i]
		// Match "1 SAMPLE" or "1. SAMPLE" — the number label before the last name
		const lastMatch = line.match(/^1\s+([A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+)*)/)
		if (lastMatch && !aamvaLastName) {
			aamvaLastName = lastMatch[1].trim()
			continue
		}
		// Match "2 JANICE" — the number label before the first name
		const firstMatch = line.match(/^2\s+([A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+)*)/)
		if (firstMatch && !aamvaFirstName) {
			aamvaFirstName = firstMatch[1].trim()
			continue
		}
		// Match "8 123 NORTH STREET" — address
		const addrMatch = line.match(/^8\s+(.+)$/)
		if (addrMatch && aamvaAddress.length === 0) {
			aamvaAddress.push(addrMatch[1].trim())
			// Next line might be city/state/zip
			if (i + 1 < linesRaw.length && /^[A-Za-z]/.test(linesRaw[i + 1])) {
				aamvaAddress.push(linesRaw[i + 1].trim())
			}
		}
	}

	// Strategy B: Look for keyword-labeled lines ("LN: SAMPLE", "FN: JANICE")
	if (!aamvaLastName) {
		const lnMatch = text.match(/(?:LN|LAST\s*NAME|SURNAME)\s*[:.]?\s*([A-Z][A-Za-z-]+)/i)
		if (lnMatch) aamvaLastName = lnMatch[1].trim()
	}
	if (!aamvaFirstName) {
		const fnMatch = text.match(/(?:FN|FIRST\s*NAME|GIVEN\s*NAME)\s*[:.]?\s*([A-Z][A-Za-z-]+)/i)
		if (fnMatch) aamvaFirstName = fnMatch[1].trim()
	}

	// Strategy C: Look for ALL-CAPS words that are likely names (on US DLs names are always uppercase)
	if (!aamvaLastName && !aamvaFirstName) {
		const noiseWords = new Set([
			'california',
			'texas',
			'florida',
			'new',
			'york',
			'illinois',
			'ohio',
			'arizona',
			'usa',
			'driver',
			'license',
			'licence',
			'identification',
			'card',
			'state',
			'department',
			'public',
			'safety',
			'dln',
			'dob',
			'exp',
			'iss',
			'sex',
			'eyes',
			'hair',
			'hgt',
			'wgt',
			'class',
			'end',
			'rest',
			'restrictions',
			'donor',
			'none',
			'brn',
			'blk',
			'blu',
			'grn',
			'hzl',
			'sample',
			'specimen',
			'duplicate',
			'north',
			'south',
			'east',
			'west',
			'street',
			'avenue',
			'road',
			'drive',
			'sacramento',
			'golden',
			'iss',
			'the',
		])

		// Find lines that are purely uppercase alpha text ≥ 4 chars and aren't noise
		const nameLines = []
		for (const line of linesRaw) {
			const cleaned = line.replace(/[^A-Za-z\s]/g, '').trim()
			if (cleaned.length < 3) continue
			if (/^[A-Z\s]+$/.test(cleaned)) {
				const words = cleaned
					.split(/\s+/)
					.filter((w) => w.length >= 2 && !noiseWords.has(w.toLowerCase()))
				if (words.length > 0) {
					nameLines.push(words.join(' '))
				}
			}
		}

		if (nameLines.length >= 2) {
			// US DL: first line is last name, second is first name
			aamvaLastName = nameLines[0]
			aamvaFirstName = nameLines[1]
		} else if (nameLines.length === 1) {
			// Single name line — could be "JANICE SAMPLE" on one line
			const words = nameLines[0].split(/\s+/)
			if (words.length >= 2) {
				aamvaFirstName = words[0]
				aamvaLastName = words.slice(1).join(' ')
			} else {
				aamvaFirstName = nameLines[0]
			}
		}
	}

	// Compose the final name
	if (aamvaFirstName || aamvaLastName) {
		const combined = `${aamvaFirstName} ${aamvaLastName}`.trim()
		result.name = combined
			.split(' ')
			.map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
			.join(' ')
		const parts = result.name.split(/\s+/)
		if (parts.length > 1) {
			result.lastName = parts.pop()
			result.firstName = parts.join(' ')
		} else {
			result.firstName = result.name
		}
	}

	// 4. Extract Address
	if (aamvaAddress.length > 0) {
		result.address = aamvaAddress.join(', ')
	} else {
		// Try keyword-labeled address
		const addrPatterns = [
			/(?:address|addr|add)\s*[:.]?\s*([^\n]+(?:\n[^\n]+){0,2})/i,
			/\b8\s+(\d+[^0-9\n][^\n]+)/, // "8 123 NORTH STREET"
		]
		for (const pat of addrPatterns) {
			const m = text.match(pat)
			if (m) {
				result.address = m[1].replace(/\n/g, ', ').trim()
				break
			}
		}
		// Fallback: find a line with a street number
		if (!result.address) {
			for (const line of linesRaw) {
				if (
					/^\d+\s+[A-Za-z]+\s+(?:ST|STREET|AVE|AVENUE|RD|ROAD|DR|DRIVE|BLVD|CT|LN|WAY|PL|CIR)/i.test(
						line
					)
				) {
					result.address = line.trim()
					break
				}
			}
		}
	}

	return result
}
