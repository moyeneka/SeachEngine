<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">


    <!--CSS Styles -->
    <link rel="stylesheet" href="assets/css/styles.css" />
    <title>Search Engine for Dictionary</title>
  </head>
  <body>
  <div class="container-fluid">

<nav class="navbar sticky-top navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">

        <a class="navbar-brand" style="font-size='30px'; " href="#">
        <h3>Welcome to the Search Engine</h3></a>
      </div>
</nav>
<?php
if (isset($_POST['submit'])) 
{
    print_form();
    process_query();
   

       
}
else
{
    print_form();
}

function process_query()
{ 
  // replace ' ' with '\ ' in the strings so they are treated as single command line args
 echo "<h6>Your Last Searched Query information: " . $_POST[QUERY]."</h6>"; 
 $QUERY = escapeshellarg($_POST[QUERY]);

 //$command = 'python3 accumulator.py' . ' ' .$NAME. ' '. $DIR;
 $command = 'python3 accumulator.py ' . '-q' .$QUERY;
  //remove dangerous characters from command to protect web server
  $escaped_command = escapeshellcmd($command);
  //echo "<p>command: $command <p>"; 
  //echo "<p>escapeshellcmd: $escaped_command <p>";
  // run insert_new_item.py
  system($escaped_command);         
}
//------------------------------------------------------
// This is the function that prints the form
//------------------------------------------------------
function print_form()
{
echo <<< END
<div class="card-body">
 <form method="post" action="" >
      <div class="mb-3 row">
          <div class="col-sm-5">
          <input type="text" class="form-control" id="QUERY" name="QUERY" placeholder="Enter Query" required>
              <div class="invalid-feedback">
                  Please enter query
              </div>
              <input name = "submit" type= "submit" class="form-control" value = "Search" >
          </div>
      </div>
    </form>
    <br><br>
</div>
END;
}
?>  
</body>
</html>