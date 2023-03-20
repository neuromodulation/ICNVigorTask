#ifndef __AO_GAP_LOGGER_H__
#define __AO_GAP_LOGGER_H__

#include "AOTypes.h"
#include "AOMFCDebug.h"

namespace NS_AO_MFC
{

//////////////////////////////////////////////////////////////////
// class CAOGapLogger - Log data gaps for continuous channels, i.e. SPK/LFP/RAW

class CAOGapLogger
{
public:
	CAOGapLogger(int nChannelId, CAODebug *pDebug);
	~CAOGapLogger();

	void Reset();
	void TraceGap(int16 *pStream, int nSize, int nLine, const char* strFileName);

private:
	CAODebug *m_pDebug;
	int       m_nChannelId; // The channel to trace its gaps
	uint32    m_uNextTS;
};

} // namespace NS_AO_MFC

#endif
