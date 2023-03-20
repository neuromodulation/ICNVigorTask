#include "stdafx.h"
#include "AOMFCGapLogger.h"
#include "StreamFormat.h"

namespace NS_AO_MFC
{

//////////////////////////////////////////////////////////////////
// class CAOGapLogger - Log data gaps for continuous channels, i.e. SPK/LFP/RAW

CAOGapLogger::CAOGapLogger(int nChannelId, CAODebug *pDebug)
{
	m_nChannelId = nChannelId;
	m_pDebug     = pDebug;

	Reset();
}

CAOGapLogger::~CAOGapLogger()
{
}

void CAOGapLogger::Reset()
{
	m_uNextTS = 0;
}

void CAOGapLogger::TraceGap(int16 *pStream, int nSize, int nLine, const char* strFileName)
{
	while (nSize > 0)
	{
		// 1. Get current stream
		StreamBase *pSB = (StreamBase*)pStream;

		// 2. Hop to next stream
		pStream = pStream + pSB->uSizeInWords;
		nSize  -= pSB->uSizeInWords;

		if (pSB->cType != 'd')
			continue;

		StreamDataBlock *pDataBlock = (StreamDataBlock*)pSB;
		if (pDataBlock->nChannelNumber != m_nChannelId)
			continue;

		uint32 uBlockTS = pDataBlock->uTimeStamp;
		if (m_uNextTS == 0)
			m_uNextTS = uBlockTS;

		if (uBlockTS != m_uNextTS)
		{
			// TRACE gap
			m_pDebug->Trace(nLine, strFileName,
				"Channel [%d] Expected TS [%u] Block TS [%u]", m_nChannelId, m_uNextTS, uBlockTS);
		}

		int nSamples = pDataBlock->uSizeInWords - sizeofInWords(StreamDataBlock);
		m_uNextTS = pDataBlock->uTimeStamp + nSamples;
	}
}

} // namespace NS_AO_MFC
