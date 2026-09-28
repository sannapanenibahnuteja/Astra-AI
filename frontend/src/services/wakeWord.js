const WAKE_WORDS = [
  "hey bob",
  "hey bob",
  "bob",
  "astro"
];


export function detectWakeWord(text) {


  const input =
    text
      .toLowerCase()
      .trim();



  for (const word of WAKE_WORDS) {


    if (input.includes(word)) {


      return {

        detected: true,


        command:
          input
          .replace(word, "")
          .trim()

      };

    }

  }



  return {

    detected:false,

    command:""

  };

}