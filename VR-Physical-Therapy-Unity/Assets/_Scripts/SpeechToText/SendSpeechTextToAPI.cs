using System;
using System.Collections;
using System.Collections.Generic;
using OpenAI;
using UnityEngine;
using UnityEngine.Networking;

public class SendSpeechTextToAPI : MonoBehaviour
{
    private string databaseURL = "https://la-hacks-2024-e09c3-default-rtdb.firebaseio.com/";
    
    public static event Action OnFinishedWritingToDatabase;
    
    private void OnEnable()
    {
        WhisperVoice.OnEndRecording += WriteToDatabase;
    }
    
    private void OnDisable()
    {
        WhisperVoice.OnEndRecording -= WriteToDatabase;
    }
    
    private void WriteToDatabase(string text)
    {
        StartCoroutine(WriteToDatabaseCoroutine(text));
    }

    private IEnumerator WriteToDatabaseCoroutine(string text)
    {
        // Example data
        var jsonData = "{\"speech_text\": \"" + text + "\"}";
        using (UnityWebRequest www = UnityWebRequest.Put(databaseURL + "output.json", jsonData))
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
        
        // Now we can read from the database
        OnFinishedWritingToDatabase?.Invoke();
    }
}
