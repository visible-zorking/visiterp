import React from 'react';
import { useRef, useContext, useEffect } from 'react';

import { ObjectData } from './gametypes';
import { gamedat_ids, gamedat_object_ids, gamedat_roominfo_names } from '../custom/gamedat';

import { ReactCtx } from './context';
import { ZStatePlus } from './zstate';

export type OptPosition = { x:number, y:number } | null;

export type ExtraToggle = { id:string, class?:string, transform?:string };
type ExtraToggleFunc = (zstate:ZStatePlus) => ExtraToggle[];

export function GameMap({ mobiles, extras }: { mobiles:number[], extras?:ExtraToggleFunc })
{
    let scrollref = useRefDiv();
    let mapref = useRefObject();
    
    let rctx = useContext(ReactCtx);
    let zstate = rctx.zstate;

    let dragstart: OptPosition = null;
    let scrollstart: OptPosition = null;

    let origdocsize: { w:number, h:number } = gamedat_ids.MAP_DOCSIZE;
    let viewsize: { w:number, h:number } = gamedat_ids.MAP_VIEWSIZE;
    let docsize: { w:number, h:number } = { w:0.8*origdocsize.w, h:0.8*origdocsize.h };
    
    function evhan_mousedown(ev: PointerEv) {
        if (!scrollref.current) {
            return;
        }
        /* Clip the drag area to inside the scrollbar box. (Firefox would
           allow this handler to snipe scrollbar dragging.) */
        let offx = ev.nativeEvent.offsetX;
        let offy = ev.nativeEvent.offsetY;
        if (offx < 0 || offx >= scrollref.current.clientWidth || offy < 0 || offy >= scrollref.current.clientHeight) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        if (scrollref.current && ev.button == 0) {
            dragstart = { x: ev.clientX, y: ev.clientY };
            scrollstart = { x: scrollref.current.scrollLeft, y: scrollref.current.scrollTop };
            scrollref.current.setPointerCapture(ev.pointerId);
        }
    }

    function evhan_mousemove(ev: PointerEv) {
        if (scrollref.current && dragstart && scrollstart) {
            ev.preventDefault();
            scrollref.current.scrollLeft = scrollstart.x - (ev.clientX - dragstart.x);
            scrollref.current.scrollTop = scrollstart.y - (ev.clientY - dragstart.y);
        }
    }

    /* This callback is used for *both* the map-load event and the useEffect
       that depends on zstate. This is because the SVG loads slightly later
       than the first useEffect invocation. */
    function select_location() {
        if (mapref.current) {
            let herenum = zstate.globals[0];  // LOCATION
            let hereobj = gamedat_object_ids.get(herenum);
            let herestr = '';
            if (hereobj) {
                herestr = hereobj.name;
            }

            let herecen: OptPosition = null;
            let roomobj = gamedat_roominfo_names.get(herestr);
            if (roomobj) {
                herecen = roomobj.center;
            }
            
            let mapdoc = mapref.current.contentDocument;
            if (mapdoc && mapdoc.rootElement) {
                let curstr = mapdoc.rootElement.getAttribute('data-curselect') ?? '';
                if (herestr != curstr) {
                    let el = mapdoc.getElementById('r-'+curstr.toLowerCase());
                    if (el) {
                        el.classList.remove('Selected');
                    }

                    el = mapdoc.getElementById('r-'+herestr.toLowerCase());
                    if (el) {
                        el.classList.add('Selected');
                        if (scrollref.current && herecen) {
                            scrollref.current.scrollLeft = herecen.x * docsize.w / viewsize.w - 0.5 * scrollref.current.clientWidth;
                            scrollref.current.scrollTop = herecen.y * docsize.h / viewsize.h - 0.5 * scrollref.current.clientHeight;
                        }
                    }

                    mapdoc.rootElement.setAttribute('data-curselect', herestr);
                }

                let mobcounts: {[key: string]: number} = {};
                for (let mobid of mobiles) {
                    // We rely on the fact that the zstate reports
                    // objects in order (1-based).
                    let zobj = zstate.objects[mobid-1];
                    if (!zobj)
                        continue;
                    let obj = gamedat_object_ids.get(mobid);
                    if (!obj)
                        continue;
                    let el = mapdoc.getElementById('mob-'+obj.name.toLowerCase());
                    if (!el)
                        continue;
                    
                    let mobcen: OptPosition = null;
                    let mobloc: ObjectData|undefined;
                    if (zobj.parent) {
                        mobloc = gamedat_object_ids.get(zobj.parent);
                        if (mobloc) {
                            let throomobj = gamedat_roominfo_names.get(mobloc.name);
                            if (throomobj) {
                                mobcen = throomobj.bottom;
                            }
                        }
                    }
                    if (mobcen && mobloc) {
                        let mobcount = mobcounts[mobloc.name] ?? 0;
                        let posx = mobcen.x + 2*mobcount;
                        let posy = mobcen.y + 4*mobcount;
                        el.classList.remove('Offstage');
                        el.setAttribute('transform', 'translate('+posx+','+posy+')');
                        mobcounts[mobloc.name] = mobcount+1;
                    }
                    else {
                        el.classList.add('Offstage');
                    }
                }

                if (extras) {
                    let extrals = extras(zstate);
                    for (let obj of extrals) {
                        let el = mapdoc.getElementById(obj.id);
                        if (!el)
                            continue;
                        if (obj.class !== undefined)
                            el.classList.value = obj.class;
                        if (obj.transform !== undefined)
                            el.setAttribute('transform', obj.transform);
                    }
                }
            }
        }
    }

    useEffect(select_location, [ zstate ]);
                                                       
    function evhan_mouseup(ev: PointerEv) {
        dragstart = null;
        scrollstart = null;
        if (scrollref.current) {
            scrollref.current.releasePointerCapture(ev.pointerId);
        }
    }

    return (
        <div className="ScrollXYContent" ref={ scrollref } onPointerDown={ evhan_mousedown } onPointerMove={ evhan_mousemove } onPointerUp={ evhan_mouseup } >
            <object className="GameMap" ref={ mapref } onLoad = { select_location } width={ docsize.w } height={ docsize.h } type="image/svg+xml" data="pic/map.svg" />
        </div>
    );
}

const useRefDiv = () => useRef<HTMLDivElement>(null);
const useRefObject = () => useRef<HTMLObjectElement>(null);
type PointerEv = React.PointerEvent<HTMLDivElement>;
