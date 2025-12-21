import React from 'react';
import { useState, useContext, createContext } from 'react';

export function ObjectAttrList({ attr } : { attr:number })
{
    return <div>Attribute list: { attr }</div>
}
