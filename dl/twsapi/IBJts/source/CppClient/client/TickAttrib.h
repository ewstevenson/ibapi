/* Copyright (C) 2013 Interactive Brokers LLC. All rights reserved.  This code is subject to the terms
 * and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable. */

#pragma once
#ifndef tickattrib_h__INCLUDED
#define tickattrib_h__INCLUDED

struct TickAttrib
{
	bool canAutoExecute;
	bool pastLimit;
};

#endif
