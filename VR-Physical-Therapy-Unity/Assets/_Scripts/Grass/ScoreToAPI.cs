using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

public class ScoreToAPI : MonoBehaviour
{
    private const string databaseURL = "https://la-hacks-2024-e09c3-default-rtdb.firebaseio.com/";
    
    private GrassGameManager grassGameManager;

    private void Start()
    {
        grassGameManager = GrassGameManager.GetInstance();
    }

    private void OnEnable()
    {
        GrassGameManager.OnGrassPlucked += WriteToDatabase;
    }
    
    private void OnDisable()
    {
        GrassGameManager.OnGrassPlucked -= WriteToDatabase;
    }
    
    private void WriteToDatabase()
    {
        StartCoroutine(WriteToDatabaseCoroutine());
    }

    IEnumerator WriteToDatabaseCoroutine()
    {
        string jsonData = "{\"score\": " + grassGameManager.Score + "}";
        
        using (UnityWebRequest www = UnityWebRequest.Put(databaseURL + "score.json", jsonData))
        {
            www.SetRequestHeader("Content-Type", "application/json");
            yield return www.SendWebRequest();
    
            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {
                Debug.Log("Write complete!");
            }
        }
    }
}
