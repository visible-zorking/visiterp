import React from 'react';
import { useState, useContext, createContext } from 'react';

import { sourcefile_presentation_list, gamedat_sourcefiles, gamedat_sourcefile_keymap, sourceloc_for_key, check_commentary } from '../custom/gamedat';

import { ReactCtx } from './context';
import { Commentary } from './widgets';

export type FileListContextContent = {
    selected: string;
    setSelected: (val:string) => void;
};

function new_context() : FileListContextContent
{
    return {
        selected: '',
        setSelected: (val) => {},
    };
}

const FileListCtx = createContext(new_context());

export function SourceFileList()
{
    const [ selected, setSelected ] = useState('');
    
    let rctx = useContext(ReactCtx);

    let withcom = check_commentary('FILES-LEGEND');

    let ells = sourcefile_presentation_list.map((name) => {
        let key = gamedat_sourcefile_keymap[name];
        if (!key) {
            return <li>{ name }: no key</li>
        }
        return (
            <SourceFile filename={ name } key={ key } filekey={ key } />
        );
    });  

    function evhan_click_background(ev: React.MouseEvent<HTMLDivElement, MouseEvent>) {
        ev.stopPropagation();
        setSelected('');
    }

    return (
        <FileListCtx.Provider value={ { selected, setSelected } }>
            <div className="ScrollContent" onClick={ evhan_click_background }>
                { (withcom ?
                   <Commentary topic={ withcom } />
                   : null) }
                <div>
                    { ells.length } source files:
                </div>
                <ul className="DataList">
                    { ells }
                </ul>
            </div>
        </FileListCtx.Provider>
    );
}

function SourceFile({ filename, filekey } : { filename:string, filekey:string })
{
    let rctx = useContext(ReactCtx);
    let ctx = useContext(FileListCtx);
    let selected = ctx.selected;

    let linecount = gamedat_sourcefiles[filename]?.length;
    let cla = 'Filename';
    if (filekey==selected)
        cla += ' Selected ';
    
    function evhan_click(ev: React.MouseEvent<HTMLLIElement, MouseEvent>) {
        ev.stopPropagation();
        ctx.setSelected(filekey);
        rctx.setLoc(sourceloc_for_key(filekey), false);
    }
    
    return (
        <li className={ cla } onClick={ evhan_click }>
            { filename } &nbsp; <i>({ linecount } lines)</i>
        </li>
    );
}
