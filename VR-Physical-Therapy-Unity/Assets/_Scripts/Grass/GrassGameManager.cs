using System;
using System.Collections;
using System.Collections.Generic;
using System.Timers;
using UnityEngine;

public class GrassGameManager : Singleton<GrassGameManager>
{
    public GameObject grassPrefab;
    public Transform grassParent;
    private int numGrass = 3;  // hardcoded for 3 grass.
    private int grassRemaining;
    
    public static event Action OnRoundStart;
    
    private DatabaseManager databaseManager;

    private void Start()
    {
        databaseManager = DatabaseManager.GetInstance();
    }

    private void OnEnable()
    {
        TimerScript.OnTimerEnd += StartNewRound;
    }
    
    private void OnDisable()
    {
        TimerScript.OnTimerEnd -= StartNewRound;
    }


    public void StartNewRound()
    {
        grassRemaining = numGrass;
        int difficulty = databaseManager.GameData.difficulty;
        print("DIFFICULT IS " + difficulty);
        
        for (int i = 0; i < numGrass; i++)
        {
            GameObject grass = Instantiate(grassPrefab, grassParent);
            float xLocation;
            if (i == 0)
            {
                xLocation = -.3f;
            }
            else if (i == 1)
            {
                xLocation = 0;
            }
            else
            {
                xLocation = .3f;
            }
            var SpawnLocation = new Vector3(xLocation, grass.transform.position.y, grass.transform.position.z);
            grass.transform.localPosition = SpawnLocation;
            grass.GetComponent<UpdateGrassWithAPI>().UpdateSizeBasedOnValue(difficulty);
            grass.GetComponent<UpdateGrassWithAPI>().UpdateZPositionBasedOnValue(difficulty);
        }
        OnRoundStart?.Invoke();
    }
    
    public void GrassDestroyed()
    {
        grassRemaining--;
        if (grassRemaining == 0)
        {
            print("All grass destroyed");
            StartNewRound();
        }
    }
}
