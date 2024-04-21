using System;
using UnityEngine;

[Serializable]
public class Exercise
{
    public int param1;
    public string param2;
}

[Serializable]
public class HighlightedMuscles
{
    public bool Flexor_carpi_ulnaris;
    public bool Biceps_Brachii;
    public bool Flexor_carpi_radialis;
    public bool Flexor_digitorum_superficialis;
    public bool Triceps_Brachii;
}

[Serializable]
public class GameData
{
    public Exercise Bicep_Builder;
    public Exercise Forearm_Flexors;
    public Exercise Push_and_Place;
    public int difficulty;
    public string game_type;
    public HighlightedMuscles highlighted_muscles;
    public bool lose;
    public int score;
    public bool win;
    public int winning_score;

    public static GameData CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<GameData>(jsonString);
    }
}