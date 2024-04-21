using UnityEngine;

public class UpdateGrassWithAPI : MonoBehaviour
{
    // given a value of 1, 2, 3, update the size based on the value
    public void UpdateSizeBasedOnValue(int value)
    {
        switch (value)
        {
            case 0:
                transform.localScale = new Vector3(2, 2, 2);
                break;
            case 1:
                transform.localScale = new Vector3(1.5f, 1.5f, 1.5f);
                break;
            case 2:
                transform.localScale = new Vector3(.75f, .75f, .75f);
                break;
            default:
                transform.localScale = new Vector3(1, 1, 1);
                break;
        }
    }
    
    // update the z position based on the value
    public void UpdateZPositionBasedOnValue(int value)
    {
        switch (value)
        {
            case 0:
                transform.position = new Vector3(transform.position.x, transform.position.y, 0);
                break;
            case 1:
                transform.position = new Vector3(transform.position.x, transform.position.y, .25f);
                break;
            case 2:
                transform.position = new Vector3(transform.position.x, transform.position.y, 0.5f);
                break;
            default:
                transform.position = new Vector3(transform.position.x, transform.position.y, 0);
                break;
        }
    }
}
