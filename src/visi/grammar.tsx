import React from 'react';
import { useState, useContext, createContext } from 'react';

import { GrammarLineData, RoutineData, gamedat_grammar_lines, gamedat_actions, gamedat_routine_addrs } from '../custom/gamedat';

import { ReactCtx } from './context';

export function GrammarTable()
{
    let counter = 0;
    let glinels = [];

    for (let gline of gamedat_grammar_lines) {
        glinels.push(
            <GrammarLine key={ counter } gline={ gline } />
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

export function GrammarLine({ gline }: { gline:GrammarLineData })
{
    let rctx = useContext(ReactCtx);

    let action = gamedat_actions[gline.action];

    function evhan_click(ev: React.MouseEvent<HTMLAnchorElement, MouseEvent>, func: RoutineData) {
        ev.preventDefault();
        rctx.setLoc(func.sourceloc, false);
    }
    
    let funcel: JSX.Element|null = null;
    let prefuncel: JSX.Element|null = null;
    if (action.acrtn) {
        let func = gamedat_routine_addrs.get(action.acrtn);
        if (!func) {
            funcel = <i>???</i>
        }
        else {
            funcel = (
                <code><a className="Src_Id" href="#" onClick={ (ev) => evhan_click(ev, func) }>{ func.name }</a></code>
            );
        }
    }
    if (action.preacrtn) {
        let func = gamedat_routine_addrs.get(action.preacrtn);
        if (!func) {
            prefuncel = <i>???</i>
        }
        else {
            prefuncel = (
                <code><a className="Src_Id" href="#" onClick={ (ev) => evhan_click(ev, func) }>{ func.name }</a></code>
            );
        }
    }
    
    return (
        <li>
            { gline.text }
            {' '}{ prefuncel }
            {' '}{ funcel }
        </li>
    );
}
