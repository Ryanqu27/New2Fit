export const LBS_PER_KG = 2.20462;

export const weightUnit = (pref: string | undefined | null) => 
    pref === 'imperial' ? 'lbs' : 'kg';

export const toDisplay = (kg: number | null | undefined, pref: string | undefined | null): string => {
    if (kg == null || isNaN(kg)) return '';
    return pref === 'imperial' ? (kg * LBS_PER_KG).toFixed(1) : kg.toFixed(1);
};

export const toStored = (val: number | string | null | undefined, pref: string | undefined | null): number | null => {
    if (val === null || val === undefined || val === '') return null;
    const num = Number(val);
    if (isNaN(num)) return null;
    return pref === 'imperial' ? num / LBS_PER_KG : num;
};
