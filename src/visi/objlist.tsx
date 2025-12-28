import React from 'react';
import { useState, useContext, createContext } from 'react';

import { gamedat_attribute_nums, gamedat_property_nums, gamedat_object_ids, check_commentary } from '../custom/gamedat';
import { ZProp, zobj_properties } from './zstate';
import { ReactCtx } from './context';
import { ObjPageLink, Commentary } from './widgets';
import { ObjPropertyList } from './objpage';

//### Support highlight-for-source!

export function ObjectAttrList({ attr } : { attr:number })
{
    let rctx = useContext(ReactCtx);
    let zstate = rctx.zstate;

    let attrdat = gamedat_attribute_nums.get(attr);
    if (!attrdat) {
        return <div>Attribute { attr } not found</div>;
    }

    let withcom: string|undefined;
    withcom = check_commentary(attrdat.name, 'ATTR');
    
    let objls = [];
    
    for (let tup of zstate.objects) {
        let obj = gamedat_object_ids.get(tup.onum);
        if (!obj)
            continue;
        
        let origattrs = zstate.origattrs.get(obj.onum) || 0;
        let curflag = (tup.attrs & (1 << (31-attr)));
        let origflag = (origattrs & (1 << (31-attr)));
        
        if (curflag || origflag) {
            let changed = false;
            let cla = '';
            if (curflag) {
                if (!origflag) {
                    changed = true;
                    cla = 'AddAttr';
                }
            }
            else {
                if (origflag) {
                    changed = true;
                    cla = 'DelAttr';
                }
            }
            
            objls.push(
                <li key={ obj.onum }>
                    { (rctx.shownumbers ?
                       <span className="ShowAddr">({ obj.onum }) </span>
                       : null) }
                    <ObjPageLink onum={ obj.onum } />
                    { (changed ?
                       <span className="ChangedNote">*</span>
                       : null) }
                    <code className={ cla }>{ obj.name }</code>
                </li>
            );
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
            { (withcom ?
               <Commentary topic={ withcom } />
               : null) }
            <div>Objects with attribute <code>{ attrdat.name }</code>:</div>
            { (objls.length ?
               <ul className="DataList">
                   { objls }
               </ul>
               : null) }
        </div>
    )
}

export function ObjectPropList({ propnum } : { propnum:number })
{
    let rctx = useContext(ReactCtx);
    let zstate = rctx.zstate;

    let propdat = gamedat_property_nums.get(propnum);
    if (!propdat) {
        return <div>Property { propnum } not found</div>;
    }

    let withcom: string|undefined;
    withcom = check_commentary(propdat.name, 'PROP');
    
    let objls = [];
    
    for (let tup of zstate.objects) {
        let obj = gamedat_object_ids.get(tup.onum);
        if (!obj)
            continue;

        //### we could have a "zobj_one_property" call and memoize that
        let props = zobj_properties(zstate.proptable, tup.onum);
        let origprops = zstate.origprops.get(tup.onum);

        let prop: ZProp|undefined;
        let index = 0;
        while (index < props.length) {
            if (props[index].pnum == propnum) {
                prop = props[index];
                break;
            }
            index++;
        }
        if (!prop)
            continue;
        
        let origprop = (origprops ? origprops[index] : undefined);
        let origvalues: number[];
        if (!origprop || origprop.pnum != prop.pnum)
            origvalues = [];
        else
            origvalues = origprop.values;
            
        objls.push(
            <li key={ obj.onum }>
                { (rctx.shownumbers ?
                   <span className="ShowAddr">({ obj.onum }) </span>
                   : null) }
                <ObjPageLink onum={ obj.onum } />
                <code>{ obj.name }</code>
                <ul className="DataList">
                    <ObjPropertyList key={ prop.pnum } pnum={ prop.pnum } values={ prop.values } origvalues={ origvalues } propislink={ false } />
                </ul>
            </li>
        );
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
            { (withcom ?
               <Commentary topic={ withcom } />
               : null) }
            <div>Objects with property <code>{ propdat.name }</code>:</div>
            { (objls.length ?
               <ul className="DataList">
                   { objls }
               </ul>
               : null) }
        </div>
    )
}
