using UnityEngine;
using UnityEngine.UI; // For UI elements. Use TMPro if using TextMeshPro.
using System;
using TMPro;

public class TimerScript : MonoBehaviour
{
    public TMP_Text timerText; // Assign this in the inspector. Use public TMP_Text if using TextMeshPro.
    private float startTime;
    private bool timerActive = false;
    
    public static event Action OnTimerEnd;

    private int maximumTime = 40; // TODO : Get this from the database.

    private void OnEnable()
    {
        GrassGameManager.OnRoundStart += BeginTimer;
    }
    
    private void OnDisable()
    {
        GrassGameManager.OnRoundStart -= BeginTimer;
    }

    public void BeginTimer()
    {
        // maximumTime = DatabaseManager.GetInstance().GameData.time
        startTime = Time.time;
        timerActive = true;
    }

    void Update()
    {
        if (timerActive)
        {
            float timePassed = Time.time - startTime;
            var timeShown = maximumTime - timePassed;
            // Format the time however you like here. This example shows minutes:seconds.
            string minutes = ((int)timeShown / 60).ToString();
            string seconds = (timeShown % 60).ToString("f2"); // "f2" formats the float with 2 decimal places.

            timerText.text = minutes + ":" + seconds;
            if (timeShown <= 0)
            {
                StopTimer();
                OnTimerEnd?.Invoke();
            }
        }
    }

    // Call this method to stop the timer
    public void StopTimer()
    {
        timerActive = false;
    }
}