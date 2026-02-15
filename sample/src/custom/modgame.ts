import { unpack_address } from '../visi/gametypes';
import { GnustoEngine } from '../visi/zstate';
import { gamedat_routine_names, gamedat_global_names, gamedat_string_map } from './gamedat';

export function show_commentary_hook(topic: string, engine: GnustoEngine): string|null
{
    return null;
}

