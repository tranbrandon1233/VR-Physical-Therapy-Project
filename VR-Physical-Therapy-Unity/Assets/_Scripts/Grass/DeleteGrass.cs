using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DeleteGrass : MonoBehaviour
{
    private Vector3 originalPosition;
    private bool isGrabbed = false;

    // Threshold for the Y-axis movement required to destroy the block
    public float destroyThreshold = 0.5f;
    
    private GrassGameManager grassGameManager;

    void Start()
    {
        // Store the original position of the grass block
        originalPosition = transform.position;
        grassGameManager = GrassGameManager.GetInstance();
    }

    void Update()
    {
        if (OVRInput.GetDown(OVRInput.Button.PrimaryHandTrigger) || OVRInput.GetDown(OVRInput.Button.SecondaryHandTrigger))
        {
            isGrabbed = true;
        }
        if (OVRInput.GetUp(OVRInput.Button.PrimaryHandTrigger) || OVRInput.GetUp(OVRInput.Button.SecondaryHandTrigger))
        {
            isGrabbed = false;
        }
        // Check if the block has been released by the player
        if (!isGrabbed)
        {
            float movedDistance = transform.position.y - originalPosition.y;
            if (movedDistance >= destroyThreshold)
            {
                // Destroy the block if moved upwards beyond the threshold
                print("Destroying grass");
                Destroy(gameObject);
                grassGameManager.GrassDestroyed();
            }
            else
            {
                // Reset the block's position if it hasn't been moved enough
                transform.position = originalPosition;
                transform.rotation = Quaternion.identity;
            }
        }
    }
}
