using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Model : MonoBehaviour
{
}

public class FFTask : Model
{
    public int Difficulty { get; set; }
    public int NumPlants { get; set; }
    public Tuple<List<int>, int, List<int>> Distance { get; set; }
    public int Size { get; set; }
    public string Handedness { get; set; }
    public int Time { get; private set; } // Maximum time allowed
    public int CurrentTime { get; set; } // Current time remaining

    public FFTask(int difficulty, int numPlants, Tuple<List<int>, int, List<int>> distance, int size, string handedness, int time)
    {
        Difficulty = difficulty;
        NumPlants = numPlants;
        Distance = distance;
        Size = size;
        Handedness = handedness;
        Time = time;
        CurrentTime = time; // Initializes current time to the max time initially
    }
}

public class BBTask : Model
{
    public int Difficulty { get; set; }
    public int TimerPerRevolution { get; set; }
    public int RevsRemaining { get; set; }
    public int Time { get; private set; } // Maximum time allowed
    public int CurrentTime { get; set; } // Current time remaining

    public BBTask(int difficulty, int timerPerRevolution, int revsRemaining, int time)
    {
        Difficulty = difficulty;
        TimerPerRevolution = timerPerRevolution;
        RevsRemaining = revsRemaining;
        Time = time;
        CurrentTime = time; // Initializes current time to the max time initially
    }
}