import React from 'react';
import { useState, useContext, createContext } from 'react';

import { GrammarLineData, gamedat_grammar_lines, gamedat_actions } from '../custom/gamedat';

import { ReactCtx } from './context';

export function GrammarTable()
{
    let counter = 0;
    let glinels = [];

    for (let gline of gamedat_grammar_lines) {
        let action = gamedat_actions[gline.action];
        glinels.push(
            <li>{ gline.text } - { action.name }</li>
        );
        counter++;
    }
    
    return (
        <div className="ScrollContent">
            <ul className="DataList">
                { glinels }
            </ul>
        </div>
    );
}
