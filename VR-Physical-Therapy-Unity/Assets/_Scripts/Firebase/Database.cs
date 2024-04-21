using System;
using System.Collections;
using System.Collections.Generic;
using Proyecto26;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

public class Database : MonoBehaviour
{
    private string databaseURL = "https://la-hacks-2024-e09c3-default-rtdb.firebaseio.com/";
    private string username = "tranbrandon1233";
    private string email = "tranbrandon1233@gmail.com";
    private string name = "LAHacksUser123";
    private User user = new User();
    
    // Now I want to do this via a REST API natively and not use Proyecto26
    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(WriteToDatabase());
    }
    
    IEnumerator WriteToDatabase()
    {
        // Example data
        // string jsonData = "{\"name\": \"Unity User\", \"score\": 10}";
        user.UserName = username;
        user.Email = email;
        string jsonData = JsonUtility.ToJson(user);
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
        StartCoroutine(ReadFromDatabase());
    }
    
    IEnumerator ReadFromDatabase()
    {
        using (UnityWebRequest www = UnityWebRequest.Get(databaseURL + "users/user_id.json"))
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
                var printedUser = JsonUtility.FromJson<User>(jsonData);
                Debug.Log("User: " + printedUser.UserName + " " + printedUser.Email);
                
            }
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
