#ifndef __AO_DEBUG_h__
#define __AO_DEBUG_h__

namespace NS_AO_MFC
{

//////////////////////////////////////////////////////////////////
// class CAODebug

class CAODebug
{
public:
	CAODebug();
	~CAODebug();

	void SetDebugFileName(const CString& sFileName);
	void Trace(int nLine, const char *sFileName, const char *lpszFormat, ...);

public:
	static void InitDebugFolder(CString& sFolder);
	static void DebugEnable(bool bEnable);

private:
	CString m_sFileName;
	CFile   m_file;
	BOOL    m_bOpen;

	static bool m_bEnable;
	static CString g_sFolder; // Debug folder
};

} // namespace NS_AO_MFC

#endif
