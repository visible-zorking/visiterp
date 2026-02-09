/* Convert a 16-bit Z-machine packed address into its true address value.
   For Z-machine version 3, this just means doubling it. (If we
   ever support more versions, we'll need to do more work.)
*/
export function unpack_address(val: number) : number
{
    return val * 2;
}

/* Return a 16-bit Z-machine value as a signed integer. */
export function signed_zvalue(val: number) : number
{
    return (val < 32768) ? val : (val - 65536);
}

/* Given a file key, return the sourceloc of its first line. */
export function sourceloc_for_key(filekey: string) : string
{
    return filekey + ':1:1:1:0';
}

export interface SourceFileMap {
    [key: string]: string;
}

export type SourceLoc = {
    filekey: string;
    line: number;
    char: number;
    endline: number;
    endchar: number;
};

/* Parse a sourceloc string like "C:5:1" or "C:5:1:6:0" into its component
   parts. */
export function parse_sourceloc(val: string) : SourceLoc|undefined
{
    if (!val.length)
        return undefined;

    let tup = val.split(':');
    if (tup.length < 3)
        return undefined;

    let filekey = tup[0];
    let line = parseInt(tup[1]);
    let char = parseInt(tup[2]);
    
    if (tup.length < 5) {
        return {
            filekey: filekey,
            line: line,
            char: char,
            endline: line,
            endchar: 99999
        };
    }
    
    let endline = parseInt(tup[3]);
    let endchar = parseInt(tup[4]);
    
    if (endchar == 0) {
        endline -= 1;
        endchar = 99999;
    }
    
    return {
        filekey: filekey,
        line: line,
        char: char,
        endline: endline,
        endchar: endchar
    };
}

export type ObjectData = {
    onum: number;
    name: string;
    isroom?: boolean;
    desc: string;
    propaddr: number;
    origparent: number;
    scenery?: number[];
    iscenery?: number[];
    sourceloc: string;
};

export type AttributeData = {
    name: string;
    num: number;
};

export type PropertyData = {
    name: string;
    num: number;
    vartype?: string;
};

export type GlobalData = {
    name: string;
    num: number;
    vartype?: string;
    sourceloc: string;
};

export type ConstantData = {
    name: string;
    value: number;
    sourceloc: string;
};

export type StringData = {
    text: string;
    sourceloc: string|string[];
};

export type RoutineData = {
    name: string;
    addr: number;
    argtypes?: string[];
    sourceloc: string;
};

export type DictWordData = {
    num: number;
    text: string;
    flags: string;
    prepnum?: number;
    adjnum?: number;
    verbnum?: number;
    dirnum?: number;
};

export type PrepositionData = {
    num: number;
    text: string;
    syn?: string[];
};

export type GrammarVerbData = {
    num: number;
    addr: number;
    words: string[];
    lines: GrammarLineData[];
};

export type GrammarLineData = {
    num: number;
    addr: number;
    action: number;
    clauses: GrammarClauseData[];
};

export type GrammarClauseData = {
    count?: number;
    prep?: number;
    attr?: string;
    loc?: string;
};

export type ActionData = {
    num: number;
    name: string;
    acrtn?: number;
    preacrtn?: number;
}


type CommentarySpan = string | string[];
type CommentaryLine = number | string;

export interface CommentaryMap {
    [key: string]: CommentarySpan[];
};
export interface CommentaryLineMap {
    [key: string]: CommentaryLine[];
};


export interface DistanceMap {
    [key: number]: number;
};
export interface AllDistanceMap {
    [key: number]: DistanceMap;
};

export type MapRoom = {
    name: string;
    x: number;
    y: number;
    width: number;
    height: number;
    center: { x:number, y:number };
    bottom: { x:number, y:number };
};

type SourceSpan = string | [ string, string ];
type SourceLine = SourceSpan[];

export interface SourceLinesMap {
    [key: string]: SourceLine[];
};
