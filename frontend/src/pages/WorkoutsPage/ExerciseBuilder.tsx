import { weightUnit } from '../../utils/units';

export interface ExerciseFormRow {
    name: string;
    sets: number | '';
    reps: number | '';
    weight_display: string; 
}

interface ExerciseBuilderProps {
    exerciseRows: ExerciseFormRow[];
    handleExerciseChange: (index: number, field: keyof ExerciseFormRow, value: string) => void;
    handleRemoveExercise: (index: number) => void;
    handleAddExercise: () => void;
    pref: string | undefined;
}

export default function ExerciseBuilder({
    exerciseRows,
    handleExerciseChange,
    handleRemoveExercise,
    handleAddExercise,
    pref
}: ExerciseBuilderProps) {
    return (
        <div className="exercise-builder">
            <label className="exercise-builder-label">Exercises</label>
            
            <div className="exercise-rows">
                {exerciseRows.map((row, idx) => (
                    <div key={idx} className="exercise-row">
                        <input 
                            className="ex-name" 
                            placeholder="Exercise (e.g. Bench Press)" 
                            value={row.name}
                            onChange={(e) => handleExerciseChange(idx, 'name', e.target.value)}
                            required
                        />
                        <input 
                            className="ex-sets" 
                            type="number" 
                            min="0"
                            placeholder="Sets" 
                            value={row.sets}
                            onChange={(e) => handleExerciseChange(idx, 'sets', e.target.value)}
                        />
                        <input 
                            className="ex-reps" 
                            type="number" 
                            min="0"
                            placeholder="Reps" 
                            value={row.reps}
                            onChange={(e) => handleExerciseChange(idx, 'reps', e.target.value)}
                        />
                        <div className="ex-weight-wrapper">
                            <input 
                                className="ex-weight" 
                                type="number"
                                min="0"
                                step="0.1" 
                                placeholder="Weight" 
                                value={row.weight_display}
                                onChange={(e) => handleExerciseChange(idx, 'weight_display', e.target.value)}
                            />
                            <span className="unit-badge">{weightUnit(pref)}</span>
                        </div>
                        <button 
                            type="button" 
                            className="ex-remove"
                            onClick={() => handleRemoveExercise(idx)}
                            disabled={exerciseRows.length === 1}
                            title="Remove Exercise"
                        >
                            ✕
                        </button>
                    </div>
                ))}
            </div>
            
            <button type="button" className="add-exercise-btn" onClick={handleAddExercise}>
                + Add Exercise
            </button>
        </div>
    );
}
