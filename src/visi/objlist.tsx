import React from 'react';
import { useState, useContext, createContext } from 'react';

import { gamedat_attribute_nums, gamedat_object_ids } from '../custom/gamedat';
import { ReactCtx } from './context';
import { ObjPageLink } from './widgets';

export function ObjectAttrList({ attr } : { attr:number })
{
    let rctx = useContext(ReactCtx);
    let zstate = rctx.zstate;

    let attrdat = gamedat_attribute_nums.get(attr);
    if (!attrdat) {
        return <div>Attribute { attr } not found</div>;
    }

    let objls = [];
    
    for (let tup of zstate.objects) {
        let obj = gamedat_object_ids.get(tup.onum);
        let curflag = (tup.attrs & (1 << (31-attr)));
        if (curflag && obj) {
            objls.push(
                <li key={ obj.onum }>
                    { (rctx.shownumbers ?
                       <span className="ShowAddr">({ obj.onum }) </span>
                       : null) }
                    <ObjPageLink onum={ obj.onum } />
                    <code>{ obj.name }</code>
                </li>
            )
        }
    }
    
    function evhan_click_back(ev: React.MouseEvent<HTMLAnchorElement, MouseEvent>) {
        ev.preventDefault();
        rctx.setTab('objtree');
    }

    return (
        <div className="ScrollContent">
            <div className="ObjPageBack">
                <a href="#" onClick={ evhan_click_back }>Back to World</a>
            </div>
            <div>Objects with attribute <code>{ attrdat.name }</code>:</div>
            { (objls.length ?
               <ul className="DataList">
                   { objls }
               </ul>
               : null) }
        </div>
    )
}
