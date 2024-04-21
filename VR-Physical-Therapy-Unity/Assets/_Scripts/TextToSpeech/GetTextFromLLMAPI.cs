using System;
using System.Collections;
using System.Collections.Generic;
using System.Timers;
using UnityEngine;
using UnityEngine.Networking;

public class GetTextFromLLMAPI : MonoBehaviour
{
    public static event Action<String> OnReadFromLLM;
    private string databaseURL = "https://la-hacks-2024-e09c3-default-rtdb.firebaseio.com/";
    
    private void OnEnable()
    {
        GrassGameManager.OnRoundStart += ReadFromLLM;
        SendSpeechTextToAPI.OnFinishedWritingToDatabase += ReadFromLLM;
    }
    
    private void OnDisable()
    {
        GrassGameManager.OnRoundStart -= ReadFromLLM;
        SendSpeechTextToAPI.OnFinishedWritingToDatabase -= ReadFromLLM;
    }
    
    private void ReadFromLLM()
    {
        StartCoroutine(ReadFromLLMCoroutine());
    }
    
    private IEnumerator ReadFromLLMCoroutine()
    {
        using (UnityWebRequest www = UnityWebRequest.Get(databaseURL + "llm.json"))
        {
            yield return www.SendWebRequest();
    
            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {
                string jsonData = www.downloadHandler.text;
                Debug.Log("Received data: " + jsonData);
                // Process jsonData
                var llm_text = JsonUtility.FromJson<LLMData>(jsonData);
                print("Reading LLM data from Firebase: " + llm_text.text); 
                OnReadFromLLM?.Invoke(llm_text.text);
            }
        }
    }
}

[Serializable]
public class LLMData
{
    public string text;
}
