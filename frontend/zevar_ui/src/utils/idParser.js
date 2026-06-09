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
	'DAQ', 'DCS', 'DAC', 'DCT', 'DAD', 'DBA', 'DBB', 'DBC', 'DBD', 'DAY',
	'DAG', 'DAI', 'DAJ', 'DAK', 'DAL', 'DAM', 'DCG',
	'DCS', 'DAB', 'DAU', 'DCA', 'DCB', 'DCD', 'DDE', 'DDF', 'DDG',
	'DDH', 'DDI', 'DDJ', 'DDK', 'DDL',
	'DAA', 'DAB', 'DAC', 'DAD', 'DAE', 'DAF', 'DAG', 'DAH', 'DAI',
	'DAJ', 'DAK', 'DAL', 'DAM',
	'DCE', 'DCF', 'DCG', 'DCH', 'DCI',
	'ZG', 'ZI', 'ZJ', 'ZK', 'ZL', 'ZM', 'ZN', 'ZO',
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
			if (i === valueStart || prevChar === '\n' || prevChar === ' ' || /^[A-Z0-9]$/.test(prevChar) || !prevChar) {
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
	return data.includes('<PrintLetterBarcodeData') || data.includes('PrintLetterBarcodeData') || data.includes('Aadhaar') || /uid="\d{12}"/i.test(data)
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

	// 1. Extract Aadhaar number (12 digits, optionally space-separated)
	const uidMatch = text.match(/\b\d{4}\s\d{4}\s\d{4}\b/) || text.match(/\b\d{12}\b/)
	if (uidMatch) {
		result.idNumber = uidMatch[0].replace(/\s/g, '')
	}

	// 2. Extract DOB (format DD/MM/YYYY or DD-MM-YYYY)
	const dobMatch = text.match(/\b\d{2}[-/]\d{2}[-/]\d{4}\b/)
	if (dobMatch) {
		const cleanDob = dobMatch[0].replace(/\//g, '-')
		const parts = cleanDob.split('-')
		if (parts.length === 3 && parts[2].length === 4) {
			result.dob = `${parts[2]}-${parts[1]}-${parts[0]}`
		}
	}

	// 3. Extract Name (ignore noise lines, look for clean alphabetical line)
	const lines = text.split('\n')
		.map(line => line.trim())
		.filter(line => line.length > 2)

	const noiseWords = [
		'government', 'india', 'bharat', 'sarkar', 'aadhaar', 'unique', 'identification',
		'authority', 'male', 'female', 'dob', 'birth', 'yob', 'year', 'enrollment', 'help'
	]

	let nameCandidate = ''
	for (let i = 0; i < lines.length; i++) {
		const lineLower = lines[i].toLowerCase()
		if (noiseWords.some(word => lineLower.includes(word))) {
			continue
		}
		if (/\d{4}\s\d{4}\s\d{4}/.test(lines[i]) || /^\d{12}$/.test(lines[i])) {
			continue
		}
		// First alphabetical line with capitalized words is the name
		if (/^[A-Z][a-zA-Z]*(\s+[A-Z][a-zA-Z]*)*$/.test(lines[i])) {
			nameCandidate = lines[i]
			break
		}
	}

	if (nameCandidate) {
		result.name = nameCandidate
		const parts = nameCandidate.split(/\s+/)
		if (parts.length > 1) {
			result.lastName = parts.pop()
			result.firstName = parts.join(' ')
		} else {
			result.firstName = nameCandidate
		}
	}

	return result
}


