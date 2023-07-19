import streamlit as st
import os
import imageio
import tensorflow as tf
from utils import load_data, num_to_char
from modelutil import load_model
from ffmpeg import FFmpeg

st.set_page_config(layout='wide')

st.title('LipNet')
col11, col22 = st.columns(2)
options = os.listdir(os.path.join('..', 'data', 's1'))
selected_video = st.selectbox("Chose Video", options)
col1, col2 = st.columns(2)

with col11:
    st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")

with col22:
    st.info(
        "This model is used to convert speech to text. This model has been trained with over 100 videos. ")
    st.info(
        "I have used TensorFlow,numPy,OpenCV, keras and Streamlit to build this app.")
    st.info("It can be used to convert speech to text in real time.")


if options:
    with col1:
        st.info(
            "The video display's the speech which is ready to be converted to text.")
        file_path = os.path.join('..', 'data', 's1', selected_video)
        ffmpeg = (
            FFmpeg()
            .option("y")
            .input(file_path)
            .output(
                "test_video.mp4",
                {"codec:v": "libx264"},
                vf="scale=1280:-1",
                preset="veryslow",
                crf=24,
            )
        )

        ffmpeg.execute()

        # display the video
        video = open('test_video.mp4', 'rb')
        video_bytes = video.read()
        st.video(video_bytes)

    with col2:
        st.info("This is the input for the ml model")
        video, annotations = load_data(tf.convert_to_tensor(file_path))
        # Normalize pixel values to [0, 8] and convert to uint8 data type
        image_data = tf.clip_by_value(video, 0.0, 9.0)
        # Scale to uint8 range (0-255)
        image_data = tf.cast(image_data * 50, tf.uint8)
        # increase brightness of the image
        image_data = tf.image.adjust_brightness(image_data, 0.3)
        # increase contrast of the image
        image_data = tf.image.adjust_contrast(image_data, 1.5)
        # Convert the tensor data to a list of NumPy arrays for each frame
        frames = [frame.numpy()[:, :, 0] for frame in tf.unstack(image_data)]
        imageio.mimsave('animation.gif', frames)
        # imageio.mimsave('animation.gif', video, duration=20)
        st.image('animation.gif', width=400)

        st.info("Output of model in tokens")
        model = load_model()
        yhat = model.predict(tf.expand_dims(video, axis=0))
        decoder = tf.keras.backend.ctc_decode(
            yhat, [75], greedy=True)[0][0].numpy()
        st.text(decoder)

        st.info("The decoded text")
        converted_prediction = num_to_char(decoder)
        st.text(tf.strings.reduce_join(
            converted_prediction).numpy().decode('utf-8'))

# footer
link_text = "Made with ❤️ by Aaron Jevil Nazareth"
link_url = "https://github.com/jevil25/"
link = f'<a href="{link_url}" style="display: block; text-align: center; padding: 10px; border: 2px solid #172c43; background-color:#172c43; border-radius:5px;">{link_text}</a>'
st.write(link, unsafe_allow_html=True)