import React from 'react';
import { useState, useContext, createContext } from 'react';

import { ObjectData } from './gametypes';
import { check_commentary } from './combuild';
import { gamedat_object_ids, gamedat_object_room_ids, gamedat_object_global_ids } from '../custom/gamedat';
import { gamedat_ids } from '../custom/gamedat';
import { ZObject } from './zstate';

import { ReactCtx } from './context';
import { ObjPageLink, Commentary } from './widgets';
import { ObjListSorter, sorter_for_key, contains_label } from '../custom/cwidgets';

type ObjTreeContextContent = {
    map: Map<number, ZObject>;
    selected: number;
    setSelected: (val:number) => void;
};

function new_context() : ObjTreeContextContent
{
    return {
        map: new Map(),
        selected: -1,
        setSelected: (val) => {},
    };
}

const ObjTreeCtx = createContext(new_context());

export function ObjectTree()
{
    const [ selected, setSelected ] = useState(-1);
    const [ followKey, setFollowKey ] = useState(0);
    
    let rctx = useContext(ReactCtx);
    let zstate = rctx.zstate;

    let withcom = check_commentary('OBJTREE-LEGEND');

    let roots: ZObject[] = [];
    let map: Map<number, ZObject> = new Map();
    for (let tup of zstate.objects) {
        map.set(tup.onum, tup);
        if (tup.parent == 0 || tup.parent == gamedat_ids.ROOMS || tup.parent == gamedat_ids.GLOBAL_OBJECTS || tup.onum == gamedat_ids.PSEUDO_OBJECT)
            roots.push(tup);
    }

    let sorter = sorter_for_key(followKey);
    sorter(roots, map);
    
    let rootls = roots.map((o) =>
        <ShowObject key={ o.onum } tup={ o } parentnum={ 0 } /> );

    function evhan_click_background(ev: React.MouseEvent<HTMLDivElement, MouseEvent>) {
        ev.stopPropagation();
        setSelected(-1);
    }

    return (
        <ObjTreeCtx.Provider value={ { map, selected, setSelected } }>
            <div className="ScrollContent" onClick={ evhan_click_background }>
                { (withcom ?
                   <Commentary topic={ withcom } />
                   : null) }
                <ObjListSorter followKey={ followKey } setFollowKey={ setFollowKey } />
                { (rctx.shownumbers ?
                   <div>
                       Object table begins at address { rctx.zstate.objtableaddr }.
                   </div>
                   : null) }
                <ul className="DataList">
                    { rootls }
                </ul>
            </div>
        </ObjTreeCtx.Provider>
    );
}

function ShowObject({ tup, parentnum } : {tup:ZObject, parentnum:number})
{
    let rctx = useContext(ReactCtx);
    let ctx = useContext(ObjTreeCtx);
    let map = ctx.map;
    let selected = ctx.selected;
    
    let onum = tup.onum;
    let obj = gamedat_object_ids.get(onum);
    if (!obj) {
        return <li>{ onum }: ???</li>;
    }

    let children: ZObject[] = [];
    if (onum != gamedat_ids.ROOMS && onum != gamedat_ids.LOCAL_GLOBALS && onum != gamedat_ids.GLOBAL_OBJECTS) {
        let childset = new Set();
        let val = tup.child;
        while (val != 0) {
            if (childset.has(val)) {
                console.log('BUG: loop in sibling chain');
                break;
            }
            let ctup = map.get(val);
            if (!ctup)
                break;
            children.push(ctup);
            childset.add(val);
            val = ctup.sibling;
        }

        if (obj.scenery) {
            for (let sval of obj.scenery) {
                let ctup = map.get(sval);
                if (!ctup)
                    break;
                children.push(ctup);
            }
        }
    }

    let label: string;
    if (obj.isroom)
        label = 'Room';
    else if (gamedat_object_global_ids.has(onum))
        label = 'Glob';
    else if (tup.parent != parentnum)
        label = 'Scen';
    else
        label = 'Item';

    let special: string = '';
    switch (onum) {
    case gamedat_ids.ROOMS:
        special = '(contains all rooms)';
        break;
    case gamedat_ids.GLOBAL_OBJECTS:
        special = '(contains all global-scoped objects)';
        break;
    case gamedat_ids.LOCAL_GLOBALS:
        special = '(contains all scenery)';
        break;
    }

    let childls = children.map((o) =>
        <ShowObject key={ o.onum } tup={ o } parentnum={ onum } /> );
    let childlabel = contains_label(obj);

    function evhan_click_select(ev: React.MouseEvent<HTMLLIElement, MouseEvent>) {
        ev.stopPropagation();
        ctx.setSelected(onum);
        let obj = gamedat_object_ids.get(onum);
        if (obj)
            rctx.setLoc(obj.sourceloc, false);
    }

    let cla = '';
    if (onum == selected)
        cla = 'Selected';
    if (obj.isroom) {
        if (cla.length)
            cla += ' ';
        cla += 'IsRoom';
    }
    
    let withcom = check_commentary(obj.name, 'OBJ');
    
    return (
        <>
            <li className={ cla } onClick={ evhan_click_select }>
                <span className={ ("ObjLabel ObjLabel"+label) }>{ label }</span>
                { (withcom ?
                   <Commentary topic={ withcom } smaller={ true } />
                   : null) }
                { (rctx.shownumbers ?
                   <span className="ShowAddr"> { onum }:</span>
                   : null) }
                <ObjPageLink onum={ onum } />
                <code>{ obj.name }</code>
                {' '}
                { ((obj.desc && obj.desc.length) ?
                   <span className="PrintString">&#x201C;{ obj.desc }&#x201D;</span>
                   :
                   <i>(nameless)</i> ) }
                { (withcom ?
                   <span className="LineExtraHeightSmall"></span>
                   : null) }
            </li>
            { (childls.length ? (
                <ul className="DataList">
                    { (childlabel.length ?
                       <li className="ContainsLabel">{ childlabel }...</li>
                       : null) }
                    { childls }
                </ul>) : null) }
            { (special.length ? (
                <ul className="DataList">
                    <li><i>{ special }</i></li>
                </ul>) : null) }
        </>
    );
}

