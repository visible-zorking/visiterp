import React from 'react';
import { useState, useContext, createContext } from 'react';

import { GrammarLineData, RoutineData, gamedat_grammar_lines, gamedat_grammar_verbnums, gamedat_actions, gamedat_routine_addrs } from '../custom/gamedat';

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

    let verb = gamedat_grammar_verbnums.get(gline.num);
    if (!verb) {
        return (<i>unknown verb: { gline.num }</i>);
    }
    
    let action = gamedat_actions[gline.action];

    function evhan_click(ev: React.MouseEvent<HTMLAnchorElement, MouseEvent>, func: RoutineData) {
        ev.preventDefault();
        rctx.setLoc(func.sourceloc, false);
    }

    let clausels = gline.clauses.map(clause => {
        let prepel: JSX.Element|null = null;
        let attrel: JSX.Element|null = null;
        if (clause.prep) {
            prepel = (
                <>
                    {' '}
                    <span className="PrintDictWord">&#x2018;{ clause.prep }&#x2019;</span>
                </>
            );
        }
        if (clause.attr) {
            attrel = (
                <>
                    :<code>{ clause.attr }</code>
                </>
            );
        }
        return (
            <>
                { prepel } <i>obj</i>{ attrel }
            </>
        );
    });
    
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
            <span className="PrintDictWord">&#x2018;{ verb.words[0] }&#x2019;</span>
            {' '}{ clausels }
            {' '}{ prefuncel }
            {' '}{ funcel }
        </li>
    );
}
