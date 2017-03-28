﻿/* Copyright (C) 2013 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
 * and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable. */

#include "StdAfx.h"
#include "EReaderOSSignal.h"
#if defined(IB_POSIX)
#if defined(__MACH__)
#include <sys/time.h>
#else
#include <time.h>
#endif
#endif

#define MS_IN_SEC 1000


EReaderOSSignal::EReaderOSSignal(unsigned long waitTimeout) throw (std::runtime_error)
{
    bool ok = false;
    m_waitTimeout = waitTimeout;
#if defined(IB_POSIX)
    int rc1 = pthread_mutex_init(&m_mutex, NULL);
    int rc2 = pthread_cond_init(&m_evMsgs, NULL);
#if defined(__MACH__)
    ok = rc1 == 0 && rc2 == 0;
#else
    pthread_condattr_t attr;
    int rc3 = pthread_condattr_init(&attr);
    int rc4 = pthread_condattr_setclock(&attr, CLOCK_MONOTONIC);
    pthread_condattr_destroy(&attr);
    ok = rc1 == 0 && rc2 == 0 && rc3 == 0 && rc4 == 0;
#endif
    open = false; 
#elif defined(IB_WIN32)
	m_evMsgs = CreateEvent(0, false, false, 0);
    ok = (NULL != m_evMsgs);
#else
#   error "Not implemented on this platform"
#endif
	if (!ok)
		throw std::runtime_error("Failed to create event");
}


EReaderOSSignal::~EReaderOSSignal(void)
{
#if defined(IB_POSIX)
    pthread_cond_destroy(&m_evMsgs);
    pthread_mutex_destroy(&m_mutex);
#elif defined(IB_WIN32)
	CloseHandle(m_evMsgs);
#else
#   error "Not implemented on this platform"
#endif
}


void EReaderOSSignal::issueSignal() {
#if defined(IB_POSIX)
    pthread_mutex_lock(&m_mutex);
    open = true;
    pthread_cond_signal(&m_evMsgs);
    pthread_mutex_unlock(&m_mutex);
#elif defined(IB_WIN32)
	SetEvent(m_evMsgs);
#else
#   error "Not implemented on this platform"
#endif
}

void EReaderOSSignal::waitForSignal() {
#if defined(IB_POSIX)
    pthread_mutex_lock(&m_mutex); 
    if (!open) {
        if ( m_waitTimeout == INFINITE ) {
            pthread_cond_wait(&m_evMsgs, &m_mutex);
        }
        else {
#if defined(__MACH__)
// on Mac OS X, clock_gettime is not available, stick to gettimeofday for the moment
            struct timespec ts;
            struct timeval tv;
            gettimeofday(&tv, NULL);
            ts.tv_sec = tv.tv_sec+m_waitTimeout/MS_IN_SEC;
            ts.tv_nsec = (m_waitTimeout%MS_IN_SEC)*1000/*us/ms*/*1000/*ns/us*/;
#else
            struct timespec ts;
            clock_gettime(CLOCK_MONOTONIC, &ts);
            ts.tv_sec += m_waitTimeout/ MS_IN_SEC;
            ts.tv_nsec += MS_IN_SEC * MS_IN_SEC * (m_waitTimeout % MS_IN_SEC);
            ts.tv_sec += ts.tv_nsec / (MS_IN_SEC * MS_IN_SEC * MS_IN_SEC);
            ts.tv_nsec %= (MS_IN_SEC * MS_IN_SEC * MS_IN_SEC);
#endif
            pthread_cond_timedwait(&m_evMsgs, &m_mutex, &ts);
        }
    }
    open = false;
    pthread_mutex_unlock(&m_mutex);
#elif defined(IB_WIN32)
	WaitForSingleObject(m_evMsgs, m_waitTimeout);
#else
#   error "Not implemented on this platform"
#endif
}
