#include "stdafx.h"
#include "AOMFCDebug.h"

#include <stdarg.h>
#include <stdio.h>
#include <ctime>

namespace NS_AO_MFC
{

CString CAODebug::g_sFolder = "c:\\SysSDKExamples_Traces\\";
bool CAODebug::m_bEnable = false;

CAODebug::CAODebug()
{
	m_bOpen = FALSE;
}

CAODebug::~CAODebug()
{
	if (m_bOpen)
	{
		m_file.Close();
		m_bOpen = FALSE;
	}
}

void CAODebug::SetDebugFileName(const CString& sFileName)
{
	if (m_bOpen)
	{	// In case file was open
		m_file.Close();
		m_bOpen = FALSE;
	}

	m_sFileName = CAODebug::g_sFolder + sFileName;
	m_bOpen = m_file.Open(m_sFileName.GetBuffer(), CFile::modeCreate | CFile::modeWrite);
}

void CAODebug::Trace(int nLine, const char *sFileName, const char *lpszFormat, ...)
{
	if (!CAODebug::m_bEnable || !m_bOpen)
		return;

	va_list args;
	va_start(args, lpszFormat);

	char sTrace[1024] = {0};
	_vsnprintf(sTrace, sizeof(sTrace), lpszFormat, args);
	va_end(args);

	// Trace Format: <date> <time> <file> <line>: Trace
	char sDateTime[80] = {0};
	time_t now = time(NULL);
	tm tmNow = *localtime(&now);
	strftime(sDateTime, sizeof(sDateTime), "%Y-%m-%d.%X", &tmNow);

	CString sBuff = __T("");
	sBuff.Format("%s line: %d file: %s: %s\n", sDateTime, nLine, sFileName, sTrace);
	m_file.Write(sBuff.GetBuffer(), sBuff.GetLength());
	m_file.Flush();
}

void CAODebug::InitDebugFolder(CString& sFolder)
{
	CAODebug::g_sFolder = sFolder;

#ifdef _WIN32
	CreateDirectory(sFolder.GetBuffer(), NULL);
#endif
}

void CAODebug::DebugEnable(bool bEnable)
{
	m_bEnable = bEnable;
}

} // namespace NS_AO_MFC
