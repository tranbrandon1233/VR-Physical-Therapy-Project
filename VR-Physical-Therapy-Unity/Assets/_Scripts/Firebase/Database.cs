using System;
using System.Collections;
using System.Collections.Generic;
using Proyecto26;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

public class DatabaseManager : Singleton<DatabaseManager>
{
    public GameData GameData;
    private const string databaseURL = "https://la-hacks-2024-e09c3-default-rtdb.firebaseio.com/";
    
    // Now I want to do this via a REST API natively and not use Proyecto26
    // Start is called before the first frame update
    void Start()
    {
        // StartCoroutine(WriteToDatabase());
        StartCoroutine(ReadFromDatabase());
    }

    private void OnDestroy()
    {
        StopAllCoroutines();
    }

    IEnumerator WriteToDatabase()
    {
        // Example data
        string jsonData = "{\"name\": \"Unity User\", \"score\": 10}";
        
        using (UnityWebRequest www = UnityWebRequest.Put(databaseURL + "users/user_id.json", jsonData))
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
    
    IEnumerator ReadFromDatabase()
    {
        while (true)
        {
            using (UnityWebRequest www = UnityWebRequest.Get(databaseURL + "api.json"))
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
                    print("Reading data from Firebase"); 
                    GameData = GameData.CreateFromJSON(jsonData);
                }
            }
            // Wait 5 seconds before reading again
            yield return new WaitForSeconds(3f);
        }
    }

    // private void Start()
    // {
    //     SaveDataToFirebase();
    //     read_data();
    // }
    //
    // public void SaveDataToFirebase()
    // {
    //     user.UserName = username;
    //     user.Email = email;
    //     RestClient.Put(databaseURL + "users/user_id.json", user);
    //     print("Data saved to Firebase");
    // }
    //
    // public void read_data()
    // {
    //     print("reading data from Firebase");
    //     RestClient.Get<User>(databaseURL + "users/user_id.json").Then(response =>
    //     {
    //         user = response;
    //         Debug.Log(user.UserName);
    //         Debug.Log(user.Email);
    //     });
    //     print("Data read from Firebase");
    // }
}
