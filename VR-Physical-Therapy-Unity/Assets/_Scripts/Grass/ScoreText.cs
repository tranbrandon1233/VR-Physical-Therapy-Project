using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.SocialPlatforms.Impl;

public class ScoreText : MonoBehaviour
{
    private TMP_Text scoreText;
    private GrassGameManager grassGameManager;

    private void Start()
    {
        grassGameManager = GrassGameManager.GetInstance();
        scoreText = GetComponent<TextMeshProUGUI>();
    }

    private void OnEnable()
    {
        GrassGameManager.OnGrassPlucked += IncrementScore;
    }
    
    private void OnDisable()
    {
        GrassGameManager.OnGrassPlucked -= IncrementScore;
    }
    
    private void IncrementScore()
    {
        UpdateScoreText(grassGameManager.Score);
    }

    private void UpdateScoreText(int score)
    {
        scoreText.text = "Score: " + score;
    }
}
